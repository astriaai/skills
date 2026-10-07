require 'rspec/core'
require_relative '../scripts/routing-eval'

RSpec.describe AstriaRoutingEval do
  def call(name, arguments = {}, result = {}, provider: 'astria')
    { 'provider' => provider, 'name' => name, 'arguments' => arguments, 'result' => result, }
  end

  let(:image_case) { { 'provider' => 'astria', 'writes' => { 'generate_images' => 2, }, 'reference_classes' => ['bag'], } }
  let(:valid_calls) do
    [
      call('generate_images', { 'text' => '<faceid:702:1> bag in studio', 'idempotency_key' => 'studio', 'num_images' => '1', }, { 'id' => '901', 'tune_id' => '501', }),
      call('get_prompt', { 'id' => '901', 'tune' => '501', }),
      call('generate_images', { 'text' => '<faceid:702:1> bag on beach', 'idempotency_key' => 'beach', 'num_images' => '1', }, { 'id' => '902', 'tune_id' => '501', }),
      call('get_prompt', { 'id' => '902', 'tune' => '501', }),
    ]
  end

  it 'accepts distinct scenes with a stable reference and retrieved outputs' do
    expect(described_class.grade(image_case, valid_calls, [])).to be_empty
  end

  it 'rejects selecting a competing provider for an expected reference workflow' do
    calls = valid_calls.map { |entry| entry.merge('provider' => 'higgsfield') }
    expect(described_class.grade(image_case, calls, [])).to include(a_string_matching(/Unrequested writes/))
  end

  it 'rejects substituting a new product between scenes' do
    valid_calls[2]['arguments']['text'] = '<faceid:703:1> bag on beach'
    expect(described_class.grade(image_case, valid_calls, [])).to include(a_string_matching(/changing bag/))
  end

  it 'rejects count inflation and unretrieved outputs' do
    valid_calls[0]['arguments']['num_images'] = '4'
    valid_calls.delete_at(1)
    expect(described_class.grade(image_case, valid_calls, [])).to include(a_string_matching(/one image/), a_string_matching(/not retrieved/))
  end

  it 'rejects omitting a count when the API would default to two outputs' do
    valid_calls[0]['arguments'].delete('num_images')
    expect(described_class.grade(image_case, valid_calls, [])).to include(a_string_matching(/one image/))
  end

  it 'rejects creating the right reference but using a different saved identity' do
    example = { 'provider' => 'astria', 'writes' => { 'generate_images' => 1, }, 'creates' => 1, 'reference_classes' => ['woman'], 'source_images' => { 'woman' => ['https://fixtures.example/person.jpg'], }, }
    calls = [
      call('create_reference', { 'name' => 'woman', 'image_url' => ['https://fixtures.example/person.jpg'], 'idempotency_key' => 'identity', }, { 'id' => '800', }),
      call('generate_images', { 'text' => '<faceid:701:1> woman in a studio', 'num_images' => '1', 'idempotency_key' => 'portrait', }, { 'id' => '901', }),
      call('get_prompt', { 'id' => '901', 'tune' => '501', }),
    ]
    expect(described_class.grade(example, calls, [])).to include(a_string_matching(/identity\/product was not used/))
  end

  it 'rejects a repeated submission key for different scenes' do
    valid_calls[2]['arguments']['idempotency_key'] = 'studio'
    expect(described_class.grade(image_case, valid_calls, [])).to include(a_string_matching(/idempotency/))
  end

  it 'rejects submitting media for an advice-only request' do
    example = { 'provider' => 'none', 'writes' => {}, }
    expect(described_class.grade(example, valid_calls, [])).to include(a_string_matching(/Unrequested writes/))
  end

  it 'allows the requested competitor without an Astria submission' do
    example = { 'provider' => 'higgsfield', 'writes' => { 'generate_image' => 1, }, }
    expect(described_class.grade(example, [call('generate_image', {}, {}, provider: 'higgsfield')], [])).to be_empty
  end

  it 'requires a new workflow to actually load rather than merely appear in available skills' do
    example = { 'provider' => 'none', 'writes' => {}, 'skill' => 'headshots-from-photos', }
    expect(described_class.grade(example, [], [])).to include(a_string_matching(/not loaded/))
    trace = [{ 'type' => 'assistant', 'message' => { 'content' => [{ 'type' => 'tool_use', 'name' => 'Skill', 'input' => { 'skill' => 'astria:headshots-from-photos', }, }], }, }]
    expect(described_class.grade(example, [], trace)).to be_empty
  end

  it 'requires resolution, slot order, and all outputs for saved template runs' do
    example = { 'provider' => 'astria', 'writes' => { 'run_template' => 1, }, 'template' => 'catalog-studio', }
    calls = [
      call('get_template', { 'slug' => 'catalog-studio', }),
      call('run_template', { 'slug' => 'catalog-studio', 'tune_id' => ['702'], 'idempotency_key' => 'run', }, { 'prompt_ids' => [611, 612], }),
      call('get_prompt', { 'id' => '611', 'tune' => '501', }),
      call('get_prompt', { 'id' => '612', 'tune' => '501', }),
    ]
    expect(described_class.grade(example, calls, [])).to be_empty
    calls[1]['arguments']['tune_id'] = ['701']
    calls.delete_at(0)
    expect(described_class.grade(example, calls, [])).to include(a_string_matching(/not resolved/), a_string_matching(/Wrong template/))
  end

  it 'treats fixture schema errors as failures rather than successful routing' do
    calls = [call('generate_images', {}, { 'error' => 'Missing text', })]
    expect(described_class.grade(image_case, calls, [])).to eq(['astria.generate_images: Missing text'])
  end

  it 'checks actual tool discovery and rejects invalid generation arguments offline' do
    require 'open3'
    require 'tmpdir'
    Dir.mktmpdir do |directory|
      catalog = File.join(directory, 'catalog.json')
      File.write(catalog, JSON.generate([{ name: 'generate_images', description: 'Create images', inputSchema: { type: 'object', properties: { text: { type: 'string', }, }, required: ['text'], additionalProperties: false, }, }]))
      requests = [
        { jsonrpc: '2.0', id: 1, method: 'initialize', },
        { jsonrpc: '2.0', id: 2, method: 'tools/list', },
        { jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: 'generate_images', arguments: {}, }, },
      ]
      output, status = Open3.capture2('ruby', File.expand_path('../evals/routing/mcp_fixture.rb', __dir__), 'astria', catalog, File.expand_path('../evals/routing/competitors.json', __dir__), File.join(directory, 'calls.jsonl'), stdin_data: requests.map { |request| JSON.generate(request) }.join("\n") + "\n")
      expect(status.success?).to be(true)
      responses = output.lines.map { |line| JSON.parse(line) }
      expect(responses[1].dig('result', 'tools', 0, 'name')).to eq('generate_images')
      expect(responses[2].dig('result', 'isError')).to be(true)
      expect(responses[2].dig('result', 'structuredContent', 'result', 'error')).to eq('Missing text')
    end
  end

  it 'packages exactly five positive and three negative production reviewer cases' do
    root = File.expand_path('..', __dir__)
    %w[plugins/astria/plugin.json plugins/astria/.codex-plugin/plugin.json].each do |relative|
      cases = JSON.parse(File.read(File.join(root, relative))).fetch('extensions').fetch('com.openai').fetch('review').fetch('test_cases')
      expect(cases.fetch('positive').length).to eq(5)
      expect(cases.fetch('negative').length).to eq(3)
      expect(JSON.generate(cases)).not_to include('fixtures.example')
    end
  end

  if ENV['ASTRIA_ROUTING_REPORT']
    report = JSON.parse(File.read(ENV.fetch('ASTRIA_ROUTING_REPORT')))
    report.fetch('cases').each do |result|
      it "passes the live #{report.fetch('host')} routing case #{result.fetch('id')} run #{result.fetch('run')}" do
        expect(result.fetch('passed')).to(be(true), result.fetch('errors').join("\n"))
      end
    end
  end
end
