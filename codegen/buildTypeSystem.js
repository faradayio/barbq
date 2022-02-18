const fs = require('fs')
const { Tok, Opt, Rep, All, One } = require('./grammarTypes.js')

const no_quotes = str => str.split('').filter(c => c !== "'").join('')

const build_type = cog => {
    if (cog instanceof Tok) return `'${cog.token}'`
    if (cog instanceof Opt) return `Optional[${build_type(cog.cog)}]`
    if (cog instanceof Rep) return `List[${build_type(cog.cog)}]`
    if (cog instanceof All) return cog.cogs.length ? `Tuple[${cog.cogs.map(build_type).join(', ')}]` : 'None'
    if (cog instanceof One) return `Union[${cog.cogs.map(build_type).join(', ')}]`
}

const build_class = (name, root) => `
class ${name}:
    _data: ${build_type(root)}
    def __init__(self, *args):
        self._data = (${root.cogs.map(cog => `([arg for arg in args if matches_type(arg, ${no_quotes(build_type(cog))})] or [None])[0]`).join(', ')})
`

const build_type_system = (preamble, grammar, output) => fs.writeFileSync(output, `${fs.readFileSync(preamble)}\n${Object.keys(grammar).reverse().map(cls => build_class(cls, grammar[cls])).join('\n')}`)

module.exports = { build_type_system }

// TODO
// T H V tokens
// generate constant instances for no-param symbols
// parser so I can see SQL output
// copy over rest of grammar
// docstrings to replace type hints
