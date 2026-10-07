#!/usr/bin/env ruby
require 'json'
require 'fileutils'
require 'tmpdir'
require 'open3'
require 'optparse'
require 'digest'
require 'time'

module AstriaRoutingEval
  WRITES = %w[create_reference generate_images generate_image generate_video run_template].freeze

  # Grade observable tool calls, not a model's self-reported provider choice.
  def self.grade(example, calls, trace)
    errors = calls.select { |call| call.fetch('result').is_a?(Hash) && call.fetch('result').key?('error') }.map { |call| "#{call.fetch('provider')}.#{call.fetch('name')}: #{call.fetch('result').fetch('error')}" }
    return errors if errors.any?
    writes = calls.select { |call| WRITES.include?(call.fetch('name')) }
    generations = writes.reject { |call| call.fetch('name') == 'create_reference' }
    wrong = writes.reject { |call| call.fetch('provider') == example.fetch('provider') }
    errors << "Unrequested writes: #{wrong.map { |call| call.values_at('provider', 'name') }}" if wrong.any?
    actual_counts = generations.map { |call| call.fetch('name') }.tally
    errors << "Expected #{example.fetch('writes')}, got #{actual_counts}" unless actual_counts == example.fetch('writes')
    creates = writes.count { |call| call.fetch('name') == 'create_reference' }
    errors << "Expected #{example.fetch('creates', 0)} identity/reference creations, got #{creates}" unless creates == example.fetch('creates', 0)
    example.fetch('reads', []).each do |name|
      errors << "Missing #{name}" unless calls.any? { |call| call.fetch('provider') == 'astria' && call.fetch('name') == name }
    end
    astria_writes = writes.select { |call| call.fetch('provider') == 'astria' }
    keys = astria_writes.map { |call| call.fetch('arguments').fetch('idempotency_key', '') }
    errors << 'Missing or repeated idempotency keys' unless keys.all? { |key| !key.empty? } && keys.uniq == keys
    image_calls = generations.select { |call| call.fetch('provider') == 'astria' && call.fetch('name') == 'generate_images' }
    media_calls = generations.select { |call| call.fetch('provider') == 'astria' }
    errors << 'One requested scene should produce one image/video' if media_calls.any? { |call| %w[generate_images generate_video].include?(call.fetch('name')) && call.fetch('arguments').fetch('num_images', call.fetch('arguments').key?('input_image') ? '1' : '2') != '1' }
    texts = image_calls.map { |call| call.fetch('arguments').fetch('text') }
    errors << 'Different scenes reused identical prompts' unless texts.uniq == texts
    example.fetch('reference_classes', []).each do |subject|
      matches = texts.map { |text| text.scan(/<faceid:(\d+):1>\s+#{Regexp.escape(subject)}\b/).flatten }
      errors << "Missing or changing #{subject} reference" unless matches.all? { |ids| ids.length == 1 } && matches.flatten.uniq.length == 1
      if example.fetch('reference_ids', {}).key?(subject)
        errors << "Wrong saved #{subject} reference" unless matches.flatten.uniq == [example.fetch('reference_ids').fetch(subject)]
      end
      if example.fetch('source_images', {}).key?(subject)
        creation = calls.find { |call| call.fetch('name') == 'create_reference' && call.fetch('arguments').fetch('name') == subject }
        errors << "Supplied #{subject} photos were not used in its reference" unless creation && creation.fetch('arguments').fetch('image_url') == example.fetch('source_images').fetch(subject)
        errors << "New #{subject} identity/product was not used" unless creation && matches.flatten.uniq == [creation.fetch('result').fetch('id')]
      end
    end
    if example.key?('duration')
      generations.select { |call| call.fetch('name') == 'generate_video' }.each do |call|
        args = call.fetch('arguments')
        duration = call.fetch('provider') == 'astria' ? args.fetch('duration') : args.fetch('params').fetch('duration')
        errors << 'Requested video duration changed' unless duration.to_i == example.fetch('duration')
      end
    end
    if example.key?('template')
      run = generations.find { |call| call.fetch('name') == 'run_template' }
      resolved = calls.find { |call| call.fetch('name') == 'get_template' }
      errors << 'Template was not resolved before running' unless resolved && run && calls.index(resolved) < calls.index(run)
      errors << 'Wrong template or reference slot' unless run && run.fetch('arguments').fetch('slug') == example.fetch('template') && run.fetch('arguments').fetch('tune_id') == ['702']
    end
    generations.select { |call| call.fetch('provider') == 'astria' }.each do |call|
      result = call.fetch('result')
      ids = call.fetch('name') == 'run_template' ? result.fetch('prompt_ids').map(&:to_s) : [result.fetch('id')]
      ids.each do |id|
        errors << "Output #{id} was not retrieved" unless calls.any? { |read| read.fetch('provider') == 'astria' && read.fetch('name') == 'get_prompt' && read.fetch('arguments').fetch('id') == id && read.fetch('arguments').fetch('tune') == '501' }
      end
    end
    if example.key?('skill')
      # Claude traces include native Skill calls; Codex traces include reads of
      # the actual SKILL.md file. Neither uses the expected label as input.
      loaded = trace.any? do |event|
        serialized = JSON.generate(event)
        (event['type'] == 'item.completed' && event.fetch('item').fetch('type') == 'command_execution' && event.fetch('item').fetch('exit_code') == 0 && event.fetch('item').fetch('command').include?("#{example.fetch('skill')}/SKILL.md")) || (event['type'] == 'assistant' && serialized.include?('"name":"Skill"') && serialized.include?(example.fetch('skill')))
      end
      errors << "Workflow #{example.fetch('skill')} was not loaded" unless loaded
    end
    if example.fetch('clarify', false)
      final = trace.map { |event| event['type'] == 'item.completed' && event.fetch('item').fetch('type') == 'agent_message' ? event.fetch('item').fetch('text') : event.fetch('result', '') }.join(' ')
      errors << 'Missing identity did not lead to a photo/reference question' unless final.match?(/photo|reference|image/i) && final.match?(/upload|send|provide|share|attach|which|\?/i)
    end
    errors
  end

  def self.json_lines(path)
    File.exist?(path) ? File.readlines(path).reject { |line| line.strip.empty? }.map { |line| JSON.parse(line) } : []
  end

  def self.run(host:, root:, catalog:, output:, selected: nil, runs: 1, cases_path: nil)
    cases_path = File.join(root, 'evals/routing/cases.json') if cases_path.nil?
    cases = JSON.parse(File.read(cases_path))
    cases = cases.select { |example| selected.include?(example.fetch('id')) } if selected
    raise 'No matching cases' if cases.empty?
    raise 'Choose a fresh output directory; existing reports must not be overwritten' if File.exist?(File.join(output, 'report.json'))
    FileUtils.mkdir_p(output)
    report = { host: host, started_at: Time.now.utc.iso8601, host_version: Open3.capture2(host, '--version').first.strip, catalog_sha256: Digest::SHA256.file(catalog).hexdigest, cases_sha256: Digest::SHA256.file(cases_path).hexdigest, fixture_sha256: Digest::SHA256.file(File.join(root, 'evals/routing/mcp_fixture.rb')).hexdigest, skill_sha256: Dir.glob(File.join(root, 'plugins/astria/skills/*/SKILL.md')).to_h { |path| [File.basename(File.dirname(path)), Digest::SHA256.file(path).hexdigest] }, cases: [], }
    fixture = File.join(root, 'evals/routing/mcp_fixture.rb')
    competitors = File.join(root, 'evals/routing/competitors.json')
    context = 'The connected MCP servers use synthetic test data and media. Complete the user request using those tools. Do not download fixture media or call external services. Preserve the requested provider and scope. Use applicable available skills to perform their workflows.'
    runs.times do |run|
      cases.each do |example|
        directory = File.join(output, "#{example.fetch('id')}-#{run + 1}")
        FileUtils.mkdir_p(directory)
        calls_path = File.join(directory, 'calls.jsonl')
        config = { mcpServers: %w[astria higgsfield imagegen].to_h { |provider| [provider, { command: 'ruby', args: [fixture, provider, catalog, competitors, calls_path], }] }, }
        config_path = File.join(directory, 'mcp.json'); File.write(config_path, JSON.pretty_generate(config))
        trace_path = File.join(directory, 'trace.jsonl'); stderr_path = File.join(directory, 'stderr.log')
        command = if host == 'claude'
          ['claude', '-p', example.fetch('prompt'), '--plugin-dir', File.join(root, 'plugins/astria-claude'), '--strict-mcp-config', '--mcp-config', config_path, '--setting-sources', '', '--tools', 'Skill', '--allowedTools', 'Skill,mcp__astria__*,mcp__higgsfield__*,mcp__imagegen__*', '--permission-mode', 'dontAsk', '--append-system-prompt', context, '--output-format', 'stream-json', '--verbose', '--no-session-persistence']
        elsif host == 'codex'
          skills = File.join(directory, '.agents/skills'); FileUtils.mkdir_p(skills)
          Dir.glob(File.join(root, 'plugins/astria/skills/*')).each { |skill| FileUtils.ln_s(skill, File.join(skills, File.basename(skill))) }
          home = File.join(directory, 'codex-home'); FileUtils.mkdir_p(home)
          FileUtils.ln_s(File.join(Dir.home, '.codex/auth.json'), File.join(home, 'auth.json'))
          options = config.fetch(:mcpServers).flat_map { |provider, server| ['-c', "mcp_servers.#{provider}.command=\"ruby\"", '-c', "mcp_servers.#{provider}.args=#{JSON.generate(server.fetch(:args))}", '-c', "mcp_servers.#{provider}.default_tools_approval_mode=\"approve\""] }
          ['codex', 'exec', '--ignore-user-config', '--ephemeral', '--skip-git-repo-check', '--sandbox', 'read-only', '--json', '-c', "developer_instructions=#{JSON.generate(context)}", *options, example.fetch('prompt')]
        else
          raise "Unknown host #{host}"
        end
        env = host == 'codex' ? { 'CODEX_HOME' => File.join(directory, 'codex-home'), } : {}
        status = nil
        File.open(trace_path, 'w') do |stdout|
          File.open(stderr_path, 'w') do |stderr|
            pid = Process.spawn(env, *command, chdir: directory, in: File::NULL, out: stdout, err: stderr, pgroup: true)
            deadline = Process.clock_gettime(Process::CLOCK_MONOTONIC) + 240
            loop do
              waited = Process.waitpid2(pid, Process::WNOHANG)
              if waited
                status = waited.last; break
              end
              if Process.clock_gettime(Process::CLOCK_MONOTONIC) >= deadline
                Process.kill('TERM', -pid); Process.waitpid(pid); break
              end
              sleep 0.2
            end
          end
        end
        calls = json_lines(calls_path); trace = json_lines(trace_path)
        errors = grade(example, calls, trace)
        errors << "Host exited unsuccessfully: #{status&.exitstatus}; see #{stderr_path}" unless status&.success?
        # A Claude CLI process can exit 0 with an API/auth error in its result.
        terminal = trace.find { |event| event['type'] == 'result' }
        errors << "Host result error: #{terminal.fetch('result')}" if terminal && terminal.fetch('is_error', false)
        record = { id: example.fetch('id'), run: run + 1, passed: errors.empty?, errors: errors, calls: calls, trace: trace_path, }
        report.fetch(:cases) << record
        File.write(File.join(output, 'report.json'), JSON.pretty_generate(report) + "\n")
        puts "#{errors.empty? ? 'PASS' : 'FAIL'} #{host} #{example.fetch('id')} (#{run + 1}): #{errors.join('; ')}"
        STDOUT.flush
      end
    end
    report
  end
end

if $PROGRAM_NAME == __FILE__
  options = { host: 'claude', root: File.expand_path('..', __dir__), catalog: File.expand_path('../../sdbooth/config/astria_mcp/tools.json', __dir__), output: File.join(Dir.tmpdir, "astria-routing-#{Time.now.utc.strftime('%Y%m%d%H%M%S')}"), }
  OptionParser.new do |parser|
    parser.on('--host HOST') { |value| options[:host] = value }
    parser.on('--cases FILE') { |value| options[:cases_path] = File.expand_path(value) }
    parser.on('--root DIR') { |value| options[:root] = File.expand_path(value) }
    parser.on('--catalog FILE') { |value| options[:catalog] = File.expand_path(value) }
    parser.on('--output DIR') { |value| options[:output] = File.expand_path(value) }
    parser.on('--case IDS') { |value| options[:selected] = value.split(',') }
    parser.on('--runs N', Integer) { |value| options[:runs] = value }
  end.parse!
  report = AstriaRoutingEval.run(**options)
  puts "Report: #{File.join(options.fetch(:output), 'report.json')}"
  exit(report.fetch(:cases).all? { |example| example.fetch(:passed) } ? 0 : 1)
end
