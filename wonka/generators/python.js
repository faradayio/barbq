const no_quotes = str => str.split('').filter(c => c !== "'").join('')

const build_type = cog => {
    if (cog instanceof T) return `'${cog.token}'`
    if (cog instanceof N) return `'${cog.token}'`
    if (cog instanceof OPT) return `Optional[${build_type(cog.cog)}]`
    if (cog instanceof REP) return `List[${build_type(cog.cog)}]`
    if (cog instanceof ALL) return cog.cogs.length ? `Tuple[${cog.cogs.map(build_type).join(', ')}]` : 'None'
    if (cog instanceof ONE) return `Union[${cog.cogs.map(build_type).join(', ')}]`
}

const build_python_class = (name, root) => `
class ${name}:
    _data: ${build_type(root)}
    def __init__(self, *args):
        self._data = (${root.cogs.map(cog => `([arg for arg in args if matches_type(arg, ${no_quotes(build_type(cog))})] or [None])[0]`).join(', ')})
`

module.exports = { build_python_class }