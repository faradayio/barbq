# barbq
Python-native SQL dialect that renders to BigQuery

Why: exposes SQL to the machinery of python

How:

Data Layer: encode the BQ CFG in typed membership-relations of python objects, write a reverse parser and reverse lexer, which can be chained to form a serializer for BQ ASTs
guiding design principle: apply the DOF provided by transforms on the CFG against the constraint of intuitive composition

UI Layer: write overloaded/pass-through constructors using Union types
guiding design principle: apply the DOF provided by python constructor definition against the looks like SQL constraint

constraints, degrees of freedom, constraints come from reliability/formalism concerns, or from UI concerns

design principles:
    there are intuitive composability options
    but, unopinionated composability
    there are looks-like-SQL constructor options
    but, unopinionated constructors

What it looks like:
# python -> SQL pair

What the internals look like:
# constructor
# 



Tradeoffs left to the user:

Your code can look like SQL; the more pythonic power you want, the more your code will look like python

You can use the constructor-overloading to make your code look like SQL; the more type validation you want, the more your code will look like type-annotated SQL

to be exported to supporting-but-linked docs

1. write megaquery->copy out chunks to named-objects/generator-func calls
2. I am lazy->I want to reuse existing chunks and easily write SQL around them

barbq objects are immutable, but support non-inplace mutations using functions named after the constructor keyword args