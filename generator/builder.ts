import { generate_classes } from "../wonka/type_system_generator";
import { T, OPT, REP, ALL, ONE } from "../wonka/grammar_builder";

const bigquery = [];

generate_classes("./preamble.py", bigquery, "./generated.py", "python");
