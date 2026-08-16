#!/usr/bin/env ruby
# frozen_string_literal: true

# Validate each sibling backend's .quixicore/backend.yaml against
# registry/backend-metadata.schema.yaml.
#
# The schema is JSON-Schema-shaped but nothing had ever run it; this is a
# hand-rolled validator for exactly the constructs the schema uses (required,
# enum, pattern, const, additional_properties, typed arrays). Runs locally —
# CI cannot see the sibling checkouts.
#
# Usage: ruby tools/check_backend_metadata.rb   # exit 1 on any violation

require "yaml"

ROOT = File.expand_path("..", __dir__)
SCHEMA = YAML.load_file(File.join(ROOT, "registry", "backend-metadata.schema.yaml")).fetch("schema")

BACKEND_DIRS = %w[
  QuixiCore-Metal QuixiCore-CUDA QuixiCore-ROCm
  QuixiCore-XPU QuixiCore-Gaudi QuixiCore-CPU
].freeze

def validate(doc, schema, path, problems)
  case schema["type"]
  when "object"
    unless doc.is_a?(Hash)
      problems << "#{path}: expected object, got #{doc.class}"
      return
    end
    (schema["required"] || []).each do |key|
      problems << "#{path}: missing required key '#{key}'" unless doc.key?(key)
    end
    props = schema["properties"] || {}
    if schema["additional_properties"] == false
      (doc.keys - props.keys).each do |extra|
        problems << "#{path}: unknown key '#{extra}'"
      end
    end
    doc.each do |key, value|
      validate(value, props[key], "#{path}.#{key}", problems) if props[key]
    end
  when "string"
    unless doc.is_a?(String)
      problems << "#{path}: expected string, got #{doc.class}"
      return
    end
    if (enum = schema["enum"]) && !enum.include?(doc)
      problems << "#{path}: '#{doc}' not in #{enum.inspect}"
    end
    if (pattern = schema["pattern"]) && doc !~ Regexp.new(pattern)
      problems << "#{path}: '#{doc}' does not match #{pattern}"
    end
    if (const = schema["const"]) && doc != const
      problems << "#{path}: '#{doc}' != required constant '#{const}'"
    end
  when "array"
    unless doc.is_a?(Array)
      problems << "#{path}: expected array, got #{doc.class}"
      return
    end
    if (min = schema["min_items"]) && doc.size < min
      problems << "#{path}: needs at least #{min} item(s)"
    end
    doc.each_with_index do |item, i|
      validate(item, schema["items"], "#{path}[#{i}]", problems) if schema["items"]
    end
  end
end

failures = 0
BACKEND_DIRS.each do |dir|
  file = File.join(ROOT, dir, ".quixicore", "backend.yaml")
  unless File.exist?(file)
    puts "#{dir}: MISSING .quixicore/backend.yaml"
    failures += 1
    next
  end
  problems = []
  validate(YAML.load_file(file), SCHEMA, dir, problems)
  if problems.any?
    failures += 1
    puts "#{dir}: FAIL"
    problems.each { |p| puts "  #{p}" }
  else
    puts "#{dir}: ok"
  end
end

puts "#{failures.zero? ? 'OK' : 'FAIL'}: backend metadata schema"
exit(failures.zero? ? 0 : 1)
