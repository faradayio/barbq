const build_typescript_class = (name, root) => `
class ${name}:
    _data: ${build_type(root)}
    def __init__(self, *args):
        self._data = (${root.cogs.map(cog => `([arg for arg in args if matches_type(arg, ${no_quotes(build_type(cog))})] or [None])[0]`).join(', ')})
`

module.exports = { build_typescript_class }