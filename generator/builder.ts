const { generate_classes } = require('../wonka/type_system_generator')
const { Type, T, OPT, REP, ALL, ONE } = require('../wonka/grammar_builder')

bigquery = [
    
]

generate_classes('./preamble.py', bigquery, './generated.py', 'python')