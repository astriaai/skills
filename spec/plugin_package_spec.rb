require 'rspec/core'
require 'digest'
require 'fileutils'
require 'json'
require 'open3'
require 'tmpdir'

RSpec.describe 'Astria Grok package' do
  around do |example|
    Dir.mktmpdir('astria-plugin-spec-') do |directory|
      @root = directory
      source = File.expand_path('..', __dir__)
      Dir.children(source).reject { |name| ['.git', '.cache', 'dist', '__pycache__'].include?(name) }.each do |name|
        FileUtils.cp_r(File.join(source, name), directory)
      end
      example.run
    end
  end

  def run_script(name, *arguments)
    stdout, stderr, status = Open3.capture3('python3', File.join(@root, 'scripts', name), *arguments, chdir: @root)
    expect(status.success?).to be(true), "#{stdout}\n#{stderr}"
    stdout
  end

  def read_json(path)
    JSON.parse(File.read(File.join(@root, path)))
  end

  it 'packages an extractable Grok and Cursor plugin deterministically' do
    run_script('sync-plugin.py')
    version = read_json('dist/marketplace/plugins/astria-grok/.grok-plugin/plugin.json').fetch('version')
    run_script('build-plugin.py', File.join(@root, 'first'), '--target', 'grok')
    run_script('build-plugin.py', File.join(@root, 'second'), '--target', 'grok')
    archive = File.join(@root, 'first', "astria-grok-#{version}.zip")
    expect(Digest::SHA256.file(archive).hexdigest).to eq(Digest::SHA256.file(File.join(@root, 'second', File.basename(archive))).hexdigest)

    _, stderr, status = Open3.capture3('python3', '-c', 'import sys, zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])', archive, File.join(@root, 'extracted'))
    expect(status.success?).to be(true), stderr
    cursor = read_json('extracted/.cursor-plugin/plugin.json')
    expect(read_json('extracted/.grok-plugin/plugin.json').fetch('name')).to eq('astria')
    expect(File.directory?(File.join(@root, 'extracted', cursor.fetch('skills')))).to be(true)
    expect(read_json(File.join('extracted', cursor.fetch('mcpServers')))).to eq(read_json('extracted/.mcp.json'))
    expect(File.binread(File.join(@root, 'extracted', cursor.fetch('logo')))).to eq(File.binread(File.join(@root, 'dist/marketplace/plugins/astria/assets/logo.png')))
    expect(File.exist?(File.join(@root, 'extracted/bin'))).to be(false)
  end

  it 'updates both host manifests and marketplace versions during a release' do
    run_script('set-plugin-version.py', '9.8.7')
    run_script('sync-plugin.py')
    run_script('validate-plugin.py', '--expected-version', '9.8.7')
    expect(read_json('dist/marketplace/plugins/astria-grok/.grok-plugin/plugin.json').fetch('version')).to eq('9.8.7')
    expect(read_json('dist/marketplace/plugins/astria-grok/.cursor-plugin/plugin.json').fetch('version')).to eq('9.8.7')
    ['grok', 'cursor'].each do |host|
      entry = read_json("dist/marketplace/.#{host}-plugin/marketplace.json").fetch('plugins').first
      expect(entry.fetch('version')).to eq('9.8.7')
      expect(entry.fetch('name')).to eq('astria')
    end
  end

  it 'rejects a package connecting Cursor to a different MCP server' do
    run_script('sync-plugin.py')
    File.write(File.join(@root, 'dist/marketplace/plugins/astria-grok/mcp.json'), JSON.generate({ mcpServers: { astria: { url: 'https://wrong.example/mcp', }, }, }))
    stdout, stderr, status = Open3.capture3('python3', File.join(@root, 'scripts/validate-plugin.py'))
    expect(status.success?).to be(false)
    expect(stdout + stderr).to include('Grok mcp.json is stale')
  end

  it 'rejects a marketplace that points outside the generated plugin' do
    run_script('sync-plugin.py')
    marketplace = read_json('dist/marketplace/.grok-plugin/marketplace.json')
    marketplace.fetch('plugins').first['source']['path'] = './wrong-plugin'
    File.write(File.join(@root, 'dist/marketplace/.grok-plugin/marketplace.json'), JSON.generate(marketplace))
    stdout, stderr, status = Open3.capture3('python3', File.join(@root, 'scripts/validate-plugin.py'))
    expect(status.success?).to be(false)
    expect(stdout + stderr).to include('grok marketplace source is incorrect')
  end
end
