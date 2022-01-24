Query(
                    SELECT=[
                        Col(f"{pspec_table}.fdy_household_id", AS="fdy_household_id"),
                        Col.raw(f"'{self.source_table.id}' AS fdy_dataset_id"),
                    ]
                    + [
                        Col(f"{pspec_table}.{pcol}", AS=pcol)
                        for pcol in all_placespec_columns
                        if pcol in self.placespec_columns
                    ]
                    + [
                        Col.raw(f"NULL AS {pcol}")
                        for pcol in all_placespec_columns
                        if pcol not in self.placespec_columns
                    ],
                    FROM=Table(loose_match_from_sql, AS="loose_match")
                    JOIN=Join(
                        Table(proxy_table_name, AS="proxy"),
                        ON=f"loose_match.{join_col}=proxy.{join_col}",
                    ),
                )

basic_query = Query(
    SELECT=[
        Col("grannies.name", AS="who"),
        Col("specialty"),
        Col("grannies.hobby"),
    ],
    FROM=Table("acceptance-237317.kirby.grandmothers", AS="grannies"),
)

grandmothers = Table("acceptance-237317.kirby.grandmothers")
ref_scores = Table("acceptance-237317.kirby.ref_scores")

complex_query = Query(
    WITH=[
        Query(
            WITH=[
                Query(
                    SELECT=[
                        Col("name"),
                        Col.raw(
                            "CAST(hilda AS float64) + CAST(cookies AS float64) + CAST(knitting AS float64) AS hilda_score"
                        ),
                        Col.raw(
                            "CAST(mary AS float64) + CAST(bread as float64) + CAST(hockey AS float64) AS mary_score"
                        ),
                    ],
                    FROM=grandmothers,
                    AS="summary_scores",
                )
            ],
            SELECT=[
                Col("grannies.name", AS="name"),
                Col("hilda_score"),
                Col("mary_score"),
            ],
            FROM=grandmothers.AS("grannies"),
            JOIN=("summary_scores", On("summary_scores.name=grannies.name")),
            AS="scored_grandmas",
        ),
        Query.raw(
            f"combos AS (SELECT * FROM scored_grandmas CROSS JOIN {ref_scores.render()})"
        ),
    ],
    SELECT=[
        Col("brand"),
        Col("name", AS="granny"),
        Col.raw("relevance_score * mary_score AS score"),
    ],
    FROM="combos",
    WHERE="""
        granny='mary'
        -- for brands that care about similarity to mary, show how much they are interested in each of our grandmothers
    """,
)


# from uuid import uuid4

# source_table_id = uuid4()
# placespec_column_infos = [
#     {"col_name": "email", "used": True},
#     {"col_name": "first_name", "used": True},
#     {"col_name": "last_name", "used": False},
# ]
# loose_match_from_sql = "lm_table"
# proxy_table_name = "p_tab"
# mpjc = "sample_col"
# do_proxy_join = False
# pspec_table = "proxy" if do_proxy_join else "loose_match"
# print(
#     Query(
#         SELECT=[
#             Col(f"{pspec_table}.fdy_household_id", AS="fdy_household_id"),
#             Col.raw(f"'{source_table_id}' AS fdy_dataset_id"),
#         ]
#         + [
#             Col(f"{pspec_table}.{psci['col_name']}", AS=psci["col_name"])
#             if psci["used"]
#             else Col.raw(f"NULL AS {psci['col_name']}")
#             for psci in placespec_column_infos
#         ],
#         FROM=Table(loose_match_from_sql, AS="loose_match"),
#         JOIN=Join(
#             Table(proxy_table_name, AS="proxy"),
#             ON=f"loose_match.{mpjc}=proxy.{mpjc}",
#         )
#         if do_proxy_join
#         else None,
#     ).render()
# )

print(complex_query.render())

# TODO
# recreate the percentile code
# move to better named file, add to branch
# work with Thibault to test on the reporting SQL

# etsy prep
# set green
# set up env to run kickoff script

training_data_id = "a"
training_data_label = "a"
training_data_table = "a"
scores_id = "c"
scores_fold = "c"
scores_score = "d"
scores_table = "e"
positive_label = "f"

# with_ = With([])

query = Query(
        WITH=[
            Query(
                SELECT=[
                    Col("*"),
                    Col(f"training.label={positive_label}", AS="label_positive"),
                ],
                FROM="training",
                INNER_JOIN=(
                    Query(
                        SELECT=[
                            Col("id"),
                            Col.raw("ANY_VALUE(fold) AS fold"),
                            Col.raw("ANY_VALUE(score) AS score"),
                        ],
                        FROM="scores",
                        GROUP_BY="id",
                        AS="joined",
                    ),
                    Using(Col("id")),
                ),
                AS="q1"
            ),
            Query(
                SELECT=[
                    Col.raw(f"* EXCEPT ({training_data_id},{training_data_label})"),
                    Col(training_data_id, AS="id"),
                    Col(training_data_label, AS="label"),
                ],
                FROM=training_data_table,
                AS="training",
            ),
            Query(
                SELECT=[
                    Col(scores_id, AS="id"),
                    Col(scores_fold, AS="fold"),
                    Col(scores_score, AS="score"),
                ],
                FROM=scores_table,
                AS="scores",
            ),
        ],
        SELECT=[Col.raw("1")],
        FROM="",
    )
print(query.render())



# A : B (D | E) (F)
# class LiterateA(SQL):
#     non_terminalB: LiterateB
#     non_terminalC: Union[LiterateD, LiterateE]
#     non_terminalF: Optional[LiterateF]
#     terminal: str

#     @override
#     def rev_parse(self) -> List[Token]:
#         pass
#     @override
#     def rev_lex(self, tokens: List[Token]) -> str/RawSql:
#         pass
#     def render(self):
#         return self.rev_lex(self.rev_parse())
# class Token:
#     text: str
#     type: identifier or special character or literal
    #https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical