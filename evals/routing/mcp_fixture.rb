# Local stdio MCP fixture. It never makes HTTP requests or creates real media.
require 'json'
provider, catalog_path, competitors_path, log_path = ARGV
catalog = JSON.parse(File.read(catalog_path))
competitors = JSON.parse(File.read(competitors_path))
references = [
  { id: '701', title: 'Maya', name: 'woman', model_type: 'faceid', orig_images: ['https://fixtures.example/maya.jpg'], },
  { id: '702', title: 'Canvas Weekender bag', name: 'bag', model_type: 'faceid', orig_images: ['https://fixtures.example/bag.jpg'], },
  { id: '703', title: 'Sienna dress', name: 'dress', model_type: 'faceid', orig_images: ['https://fixtures.example/dress.jpg'], },
]
template = { id: '601', slug: 'catalog-studio', title: 'Catalog Studio', use_multi: true, reference_class_names: ['bag'], template_tunes: [{ id: 710, name: 'bag', title: 'Template Bag', }], template_slots: [{ key: 'class-bag', label: 'Bag', filter_names: ['bag'], template_tune_ids: [710], tunes: [{ id: 710, title: 'Template Bag', name: 'bag', }], }], template_prompts: [{ id: '611', text: 'studio front', }, { id: '612', text: 'studio detail', }], costs: { bag: { cost_mc: 20000, } }, }
models = { default: 'nano-banana-2', default_tune_id: 501, models: { 'nano-banana-2' => { tune_id: 501, title: 'Nano Banana 2', default: true, }, }, default_video_model: 'seedance25_720p', video_models: { 'seedance25_720p' => { title: 'Seedance 2.5 720p', motion_control: false, needs_input_video: false, supports_last_frame: true, supports_image_references: false, supports_audio_reference: false, generates_audio: true, native_audio: false, exclusive_media_modes: false, aspect_ratios: ['16:9', '9:16', '1:1'], }, }, }
params_schema = { type: 'object', properties: { model: { type: 'string', }, prompt: { type: 'string', }, count: { type: 'integer', }, duration: { type: 'integer', }, medias: { type: 'array', items: { type: 'object', }, }, }, required: ['model'], additionalProperties: true, }
tools = case provider
when 'astria'
  catalog + [{ name: 'get_profile', description: 'Read the connected Astria account; does not create content.', inputSchema: { type: 'object', properties: {}, additionalProperties: false, }, annotations: { readOnlyHint: true, }, }]
when 'higgsfield'
  competitors.map do |tool|
    schema = tool.fetch('name') == 'models_recommend' ? { type: 'object', properties: { query: { type: 'string', }, type: { type: 'string', }, }, required: ['query'], } : { type: 'object', properties: { params: params_schema, }, required: ['params'], }
    { name: tool.fetch('name'), description: tool.fetch('description'), inputSchema: schema, }
  end
when 'imagegen'
  [{ name: 'generate_image', description: 'Create or edit an image with the built-in image generator. Use for general illustrations, images, logos, and reference-based edits, or when explicitly requested.', inputSchema: { type: 'object', properties: { prompt: { type: 'string', }, input_image: { type: 'string', }, }, required: ['prompt'], }, }]
else
  raise "Unknown fixture provider #{provider}"
end
tools = JSON.parse(JSON.generate(tools))
created = []
prompts = []
sequence = 900
STDOUT.sync = true
STDIN.each_line do |line|
  request = JSON.parse(line)
  next unless request.key?('id')
  result = case request.fetch('method')
  when 'initialize'
    { protocolVersion: '2025-03-26', capabilities: { tools: {}, }, serverInfo: { name: provider, version: 'routing-fixture', }, }
  when 'ping' then {}
  when 'tools/list' then { tools: tools, }
  when 'tools/call'
    params = request.fetch('params'); name = params.fetch('name'); arguments = params.fetch('arguments')
    definition = tools.find { |tool| tool.fetch('name') == name }
    raise "Unknown tool #{name}" unless definition
    schema = definition.fetch('inputSchema')
    errors = schema.fetch('required', []).reject { |key| arguments.key?(key) }.map { |key| "Missing #{key}" }
    errors += (arguments.keys - schema.fetch('properties').keys).map { |key| "Unknown #{key}" } if schema['additionalProperties'] == false
    schema.fetch('properties').each do |key, field|
      next unless arguments.key?(key)
      valid = { 'string' => ->(value) { value.is_a?(String) }, 'boolean' => ->(value) { [true, false].include?(value) }, 'array' => ->(value) { value.is_a?(Array) }, 'object' => ->(value) { value.is_a?(Hash) }, 'integer' => ->(value) { value.is_a?(Integer) }, }.fetch(field.fetch('type')).call(arguments.fetch(key))
      errors << "Invalid #{key}" unless valid
    end
    if errors.any?
      payload = { error: errors.join(', '), }
    elsif provider == 'astria'
      payload = case name
      when 'get_profile' then { id: '1', balance: 100, }
      when 'list_models' then models
      when 'list_workspaces' then [{ id: '7', title: 'Studio', }]
      when 'list_references'
        (references + created).select { |ref| !arguments.key?('title') || ref.fetch(:title).downcase.include?(arguments.fetch('title').downcase) }
      when 'get_reference'
        (references + created).find { |ref| ref.fetch(:id) == arguments.fetch('id') } || { error: 'Reference not found', }
      when 'create_reference'
        ref = { id: (800 + created.length).to_s, title: arguments.fetch('title'), name: arguments.fetch('name'), model_type: 'faceid', orig_images: arguments.fetch('image_url'), }
        created << ref; ref
      when 'generate_images', 'generate_video'
        sequence += 1
        prompt = { id: sequence.to_s, tune_id: '501', text: arguments.fetch(name == 'generate_images' ? 'text' : 'video_prompt'), trained_at: '2026-10-07T10:00:00Z', images: ["https://fixtures.example/output-#{sequence}.#{name == 'generate_images' ? 'jpg' : 'mp4'}"], content_types: [name == 'generate_images' ? 'image/jpeg' : 'video/mp4'], }
        prompts << prompt; prompt
      when 'list_templates' then [template]
      when 'get_template' then template
      when 'run_template'
        [611, 612].each do |id|
          prompts << { id: id.to_s, tune_id: '501', trained_at: '2026-10-07T10:00:00Z', images: ["https://fixtures.example/template-#{id}.jpg"], content_types: ['image/jpeg'], }
        end
        { status: 201, message: 'Prompts created', order: { id: 1001, total_cost_mc: 20000, }, prompt_ids: [611, 612], }
      when 'list_prompts' then prompts
      when 'get_prompt'
        prompts.find { |prompt| prompt.fetch(:id) == arguments.fetch('id') && prompt.fetch(:tune_id) == arguments.fetch('tune') } || { error: 'Prompt not found for ID and tune', }
      else raise "Unimplemented fixture tool #{name}"
      end
    else
      payload = name == 'models_recommend' ? { items: [{ id: 'gpt_image_2_5', name: 'GPT Image', }, { id: 'seedance_2_5', name: 'Seedance', }], } : { results: [{ id: 'fixture-job', status: 'completed', results: { rawUrl: 'https://fixtures.example/competitor-output.jpg', }, }], }
    end
    File.open(log_path, 'a') { |file| file.puts(JSON.generate(provider: provider, name: name, arguments: arguments, result: payload, )) }
    wrapped = provider == 'astria' && name != 'get_profile' ? { result: payload, } : payload
    { content: [{ type: 'text', text: JSON.generate(wrapped), }], structuredContent: wrapped, isError: payload.is_a?(Hash) && payload.key?(:error), }
  else
    raise "Unsupported method #{request.fetch('method')}"
  end
  puts JSON.generate(jsonrpc: '2.0', id: request.fetch('id'), result: result, )
end
