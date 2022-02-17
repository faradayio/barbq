// cd barbq
// node ./codegen/builder.js
const fs = require('fs')

const preamble = './codegen/preamble.py'
const grammar = './codegen/grammar.txt'
const generated = './codegen/generated.py'

const keywords = ['WITH', 'RECURSIVE', 'ORDER', 'BY', 'LIMIT', 'ASC', 'DESC', 'LIMIT', 'OFFSET', 'SELECT', 'STRUCT', 'VALUE', 'ALL', 'DISTINCT', 'EXCEPT', 'REPLACE', 'AS', 'FROM', 'GROUP', 'HAVING', 'QUALIFY', 'WINDOW', 'SYSTEM_TIME', 'OF', 'UNNEST', 'UNPIVOT', 'INCLUDE', 'NULLS', 'EXCLUDE', 'FOR', 'IN', 'CROSS', 'JOIN', 'INNER', 'FULL', 'OUTER', 'LEFT', 'RIGHT', 'ON', 'USING', 'FIRST', 'LAST', 'UNION', 'INTERSECT']
const dict = {
    '[': 'Optional[',
    ']': ']',
    '{': 'Union[',
    '|': ', ',
    '}': ']',
    '(': '',
    ')': ''
}
keywords.forEach(kw => {dict[kw] = 'Token'})

const classes = fs.readFileSync(grammar, 'utf8').split('\n\n').map(cls => cls.split('\n').map(line => line.split(' ')))

// list, tuple, union, keyword, nonterminal
const type = {
    optional: false,
    kind: 'tuple',
    elems: [
        {
            optional: true,
            kind: 'list',
            elems: [
                {
                    optional: false,
                    kind: 'keyword',
                    val: 'KW'
                },
                {
                    optional: false,
                    kind: 'nonterminal',
                    val: 'NonTerminal'
                }
            ]
        }
    ]
}

const build_type = tokens => tokens.map(token => dict[token] ?? token).join('')

const build_fields = cls => cls.slice(1).map(build_type).map((type, i) => `\t_field${i}: ${type}`).join('\n')
const build_serializer = cls => `
        if blah:
            pass
`
const build_constructor_signature = cls => `
a: None, b: None
`
const build_constructor_body = cls => `
        self._field1 = a
`

const build_class = cls => `
class ${cls[0][0].slice(0, -1)}(SQL):
${build_fields(cls)}
    
    def _serialize_(self):
        result = []
${build_serializer(cls)}
        return result
    
    def __init__(self, ${build_constructor_signature(cls)}):
${build_constructor_body(cls)}
`

fs.writeFileSync(generated, `${fs.readFileSync(preamble, 'utf8')}\n${classes.map(build_class).join('\n')}`)