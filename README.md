# barbq
Python-native SQL dialect that renders to BigQuery

Why: exposes SQL to the machinery of python

How:
    Data zone: encode the BQ CFG in typed membership-relations of python objects, write a reverse parser and reverse lexer, which can be chained to form a serializer for BQ ASTs

    UI zone: write overloaded/pass-through constructors using Union types to satisfy the looks-like-SQL constraint

What it looks like:
# TODO include code snippets

Tradeoffs left to the user:
    Your code can look like SQL; the more pythonic power you want, the more your code will look like python

    You can use the constructor-overloading to make your code look like SQL; the more type validation you want, the more your code will look like type-annotated SQL