const fs = require('fs')
const { T, N, REP, OPT, ONE, ALL } = require('./grammar_builder.js')
const { build_python_class, build_ruby_class, build_rust_class, build_typescript_class } = require('./generators.js')

const builders = {
    'python': build_python_class,
    'rust': build_rust_class,
    'typescript': build_typescript_class,
    'ruby': build_ruby_class
}

const generate_classes = (custom_preamble_file, grammar, output_file, language) => fs.writeFileSync(output_file, `${fs.readFileSync(custom_preamble_file)}\n${Object.keys(grammar).reverse().map(cls => builders[language](cls, grammar[cls])).join('\n')}`)

module.exports = { generate_classes }

// TODO

// T N tokens
// regex the Token constants into SQL constants

// serializer so I can see SQL output

// gather all funcs
// gather all ops
// format everything using grammar_builder
// Exp / Relation 2-input funcs

// docstrings to replace type hints

// apply misc mutations
// tests
// proliferate the preamble
// release