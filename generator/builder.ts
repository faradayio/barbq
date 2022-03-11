import { generate_classes } from "../wonka/type_system_generator";
import { T, OPT, REP, ALL, ONE, CFType } from "../wonka/grammar_builder";

const bigquery: CFType[] = [];

generate_classes("./preamble.py", bigquery, "./generated.py", "python");
