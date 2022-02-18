// cd barbq
// node ./codegen/builder.js
const fs = require('fs')
const { T, NT, OPT, REP, ALL, ONE } = require('./grammarTypes.js')

const preamble = './codegen/preamble.py'
const generated = './codegen/generated.py'

bigquery = {
    'QUERY':  ALL(
        OPT(T('WITH')),
        ONE(
            T('SELECT'),
            ALL(T('('), NT('QUERY'), T(')')),
            ALL(
                NT('QUERY'),
                ONE(
                    ALL(T('UNION'), ONE(T('ALL'), T('DISTINCT'))),
                    ALL(T('INTERSECT'), T('DISTINCT')),
                    ALL(T('EXCEPT'), T('DISTINCT'))
                ),
                NT('QUERY')
            )
        ),
        OPT(NT('ORDERBY')),
        OPT(NT('LIMIT'))
    ),
    'ORDERBY': ALL(
        T('EXP'),
        OPT(ONE(T('ASC'), T('DESC'))),
        OPT(T('NULLS'), ONE(T('FIRST'), T('LAST')))
    ),
    'LIMIT': ALL(T('EXP'), NT('OFFSET')),
    'OFFSET': ALL(T('EXP'))
}
console.log(bigquery)
console.log(ALL('test'))
// COGs: (T NT) (OPT REP) (ALL ONE)
//       string    COG    List[COG]
// test: .token   .cog   .cogs

const foo = `
class Query(SQL):
    _field0: Optional[Token]
    _field1: Union[Token, Tuple[Token, Query, Token], Tuple[Query, Union[Tuple[Token, Union[Token, Token]], Tuple[Token, Token], Tuple[Token, Token]], Query]]
    _field2: Optional[OrderBy]
    _field3: Optional[Limit]

    def _serialize(self):
        result = []
        if self._field0:
            result += [self._field0]
        if isinstance()
        return result
`

const build_type = cog => {
    if (cog.cogs) {
        return `${cog instanceof ALL ? 'Tuple' : 'Union'}[${cog.cogs.map(build_type).join(', ')}]`
    }
    if (cog.cog) {
        return `${cog instanceof OPT ? 'Optional' : 'List'}[${build_type(cog.cog)}]`
    }
    return cog instanceof T ? 'Token' : cog.token
}

const build_single_field_serializer = (cog, field) => {
    if (cog instanceof T) return `result += [${cog.token}]`
    if (cog instanceof NT) return `result += self._field${field}._serialize()`
    if (cog instanceof OPT) return `if self._field${field}:\n\tresult += self._field${field}._serialize()`
    if (cog instanceof REP) return `result += self._chain(self._field${field}, ', ')`
    if (cog instanceof ONE) return `result += self._field${field}._serialize()`
    if (cog instanceof ALL) return `result += self._chain(self._field${field}, ' ')`
}

const build_fields = all => all.cogs.map(build_type).map((type, i) => `\t_field${i}: ${type}`).join('\n')

const build_serializer = all => all.cogs.map(build_single_field_serializer).join('\n')

const build_constructor_signature = cls => `
a: None, b: None
`
const build_constructor_body = cls => `
        self._field1 = a
`

const build_class = (name, all) => `
class ${name}(SQL):
${build_fields(all)}
    
    def _serialize(self):
        result = []
${build_serializer(all)}
        return result
    
    def __init__(self, ${build_constructor_signature(all)}):
${build_constructor_body(all)}
`

fs.writeFileSync(generated, `${fs.readFileSync(preamble, 'utf8')}\n${Object.keys(bigquery).map(cls => build_class(cls, bigquery[cls])).join('\n')}`)