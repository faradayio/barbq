`barbq` is a python-native SQL dialect that renders to BigQuery

```
basic_query = Query(
    SELECT=[
        Col("grannies.name"),
        Col("specialty"),
        Col("grannies.hobby"),
    ],
    FROM=Table("project.dataset.grandmothers", AS="grannies"),
)

print(basic_query.render())
```

outputs:

```
SELECT
    `grannies`.`name`,
    'specialty`,
    `grannies`.`hobby`
FROM `project`.`dataset`.`grandmothers` AS `grannies`
```

This is useful because it exposes the logic of SQL to the machinery of python (imagine using a list comprehension as your SELECT argument) while maintaining the appearance of SQL (the Table() and Col() constructors above can be removed and the raw strings will be automatically passed to appropriate constructors).

To get started, you will want to install `pip install barbq` and `from barbq.query import Query, Table, Col, Join, Exp, etc`. Type hints are also strongly recommended, as they are one of the best ways to pick up the dialect.

See also the [user guide](docs/USER.md), [contributor guide](docs/CONTRIBUTOR.md), or even the [CFG reference](docs/CFG.md).
