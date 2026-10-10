---
name: pathtrove-best-data
description: Use when the user describes a research need or task and wants datasets recommended - "which datasets can I use for X", "find me datasets with A, B and C", "recommend data for training / validating / benchmarking ...", including a number of results (top k), an order, or access requirements. Gives the method for going from the need to recommended datasets with the table and report tools (hard conditions as filters, search broad, judge on report evidence), in the user's language. There is no plan or review step. Needs the pathtrove MCP tools (pathtrove_best_data_principles, plus table and report tools).
---

# PathTrove best-data: from a research need to recommended datasets

Use the `pathtrove-data` skill for the tools and the rules that apply everywhere (language, data version, what the plugin is for). This skill is the method for recommending datasets. Call `pathtrove_version` first (with `lang`), then `pathtrove_best_data_principles` (with `lang`): it returns the full principles, each with its reason, and a map of the schema of the installed data (which columns can filter, which hold prose only, which fields exist only in the report). There is no plan, no review and no receipt: you do the work with `table search` / `table stats` / `table fields` and `report get` / `report find`.

The four principles, in short (they are for you; in the answer, say what you did in plain words, without principle numbers, field ids or tool names):

1. **Analyse the need.** Write each condition in the user's words. A condition is hard when one structured value expresses it directly and stably; the rest is judged on the report evidence. If the user lists the hard conditions, only those are filters.
2. **Turn hard conditions into filters on the schema.** Pick the field, the value and the layer: table columns (exact values from `table fields`; `a|b` is any-of; repeated `--where` is AND) or the report layers (value, text, source). A condition with no structured column is recalled with `report find` (literal words: try Chinese, English and synonyms) and judged on the reports. A column with `filled` near 0 cannot filter.
3. **Start broad.** Fewest sure filters first. A pool of 0 or very few sends you back to the conditions once, against the user's own words (a filter standing for a judged condition, a value too wide or too narrow, AND vs OR, a value the column does not have). Change only the faulty condition; if the pool is still empty, say so and which condition cut it. Do not loosen silently.
4. **Judge on the report.** Open the report before judging. "Fits" only on evidence read there, with the field named; otherwise "cannot tell yet" and what is missing. The counts you state agree with the list ("N of M" if you opened part of the pool). Put what the user asked for first (form, grouping, order), answer in their language, cite the data version.
