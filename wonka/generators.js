const { build_python_class } = require('./generators/python.js')
const { build_ruby_class } = require('./generators/ruby.js')
const { build_rust_class } = require('./generators/rust.js')
const { build_typescript_class } = require('./generators/typescript.js')

module.exports = { build_python_class, build_ruby_class, build_rust_class, build_typescript_class }