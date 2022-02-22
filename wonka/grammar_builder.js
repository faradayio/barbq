import classy from 'classy-decorator'

@classy()
class T { constructor(token) { this.token = token } }

@classy()
class N { constructor(token) { this.token = token }}

@classy()
class REP { constructor(cog) { this.cog = cog } }

@classy()
class OPT { constructor(cog) { this.cog = cog } }

@classy()
class ONE { constructor(cogs) { this.cogs = cogs } }

@classy()
class ALL { constructor(cogs) { this.cogs = cogs } }

module.exports = { Tok, Rep, Opt, One, All, T, REP, OPT, ONE, ALL }