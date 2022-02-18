const T = token => new Tok(token)
const REP = cog => new Rep(cog)
const OPT = cog => new Opt(cog)
function ONE() { return new One(Array.from(arguments)) }
function ALL() { return new All(Array.from(arguments)) }

class Tok { constructor(token) { this.token = token } }
class Rep { constructor(cog) { this.cog = cog } }
class Opt { constructor(cog) { this.cog = cog } }
class One { constructor(cogs) { this.cogs = cogs } }
class All { constructor(cogs) { this.cogs = cogs } }

module.exports = { Tok, Rep, Opt, One, All, T, REP, OPT, ONE, ALL }