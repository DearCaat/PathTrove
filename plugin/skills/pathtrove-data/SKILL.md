---
name: pathtrove-data
description: Use for any question about computational-pathology or biomedical-imaging datasets that PathTrove can answer - finding datasets for a task, organ, stain, modality or clinical endpoint; statistics and overviews (how many datasets, counts by organ / task / license / openness, how complete a field is); checking what a dataset contains (cohort size, labels, clinical variables, splits, license, access); download feasibility and size (is it open, is an application needed, how big, how to get it, what the download test found); label structure (which label files exist, task, level, classes, splits, sample counts) and fetching raw label files. Queries the PathTrove data package (downloaded on first use and cached locally) through the pathtrove MCP tools or the `pathtrove` CLI, in Chinese or English. Not for general literature search or for non-biomedical data.
---

# PathTrove data

PathTrove is a curated, versioned database of computational-pathology resources. For each resource it holds a table row (structured fields), a resource report (each field with its value, its explanation and the primary sources it cites), a download guide with a download test record, and, for some resources, label files that map samples to task labels and splits. The data package (a versioned archive on the public Hugging Face repo `Dearcat/PathTrove`, ~14 MB) is downloaded once on first use, checked against a sha256 recorded in the plugin, cached locally and read from there.

## Structure

Commands are `pathtrove <domain> <verb>` (MCP tools `pathtrove_<domain>_<verb>`), read-only:

| Domain | Verbs | Use it for |
|---|---|---|
| `table` | `fields`, `search`, `stats` | the field catalogue; filtering, projecting, sorting resources; grouped counts and fill rates. Structured values only |
| `report` | `get`, `find` | the report fields of resources in layers value / text / source; finding a term across reports |
| `download` | `plan`, `objects`, `test`, `guide` | how to obtain a resource: access, license, links; downloadable objects and sizes; the download test record; the guide by section. It never downloads a dataset |
| `label` | `list`, `get`, `fetch` | which label files exist; task, level, classes, splits, counts; downloading a raw label file |
| `best-data` | `principles` | from a research need to recommended datasets: the method (analyse the need, filters on the schema, start broad, judge on report evidence, respect k, outside search for gaps) and a schema map; no plan or review. See the `pathtrove-best-data` skill |

Every result starts with the data version. Default output is the value layer only; `layer: "text"`, `"source"` or `"all"` adds the prose and the cited sources. `format: json` and `output: <file>` (large results go to a file, the reply is a summary) are available everywhere. 

Resources are identified by their PTD id (for example `PTD-000123`, in the `id` column of every table and label result). Cite the PTD id together with the data version; a name or Feishu record id also works as input.

## Language

Every tool and command takes `lang` (`zh` or `en`; the default comes from the environment variable `PATHTROVE_LANG`, else `zh`). **Set `lang` to the language the user writes in, on every call, and answer in that language**: the table (field names, allowed values, notes), the error messages and the report and guide text then all come in one language, so the answer never mixes two. Report and guide text is the English translation for `lang=en` when one exists and passed the translation check; otherwise the original Chinese is shown, labelled `lang=zh`, and you say so in the answer. Categorical values (organ, staining, openness, task tags ...) are shown in Chinese for `lang=zh` and in English for `lang=en`, and a filter accepts either spelling. Proper names, dataset names and quotations from primary sources stay as they are.

Write the answer for the user, not for the tools. Do not quote internal names: field ids, rule or principle numbers, tool or command names, environment variables such as `PATHTROVE_WEB`. Say in plain words what they mean ("external search was off", "the table has no structured value for race").

## Before the first query

Call `pathtrove_version` once per task (with `lang`). Keep the `data_version`, the `usage_rules` (the same rules as below in short form), the `known_limitations` and the list of values the data does not have as structured fields. The first call may take a moment: it downloads the data package. If it cannot (no network to huggingface.co), the error says how to fix it: set `HF_ENDPOINT` to a mirror, or install from a local copy of the archive with `pathtrove data install --file`; tell the user, do not work around it. Every answer built on PathTrove states the data version, because the database changes between releases and a reader must be able to reproduce the lookup.

If a PathTrove call fails, say so and report the error. Do not substitute web search for it silently: the user asked for PathTrove's curated evidence, and web results are a different kind of source.

## External search policy

`pathtrove_version` shows `external_search.PATHTROVE_WEB` (`on` by default; `off` = no external search) and the policy. In short: **PathTrove first**; go outside PathTrove only to **fill coverage gaps** (the need asks for completeness, or PathTrove returns too few or none) or when the user **explicitly asks** for outside information; never to re-check values of resources PathTrove already covers (the curated record is the evidence; "verifying" it on the web puts web prose in its place, at the cost of many calls). Report external findings in their own section, each labelled "not in PathTrove <version>, not curated", with URL and access date; never invent a value PathTrove lacks. Waste: searching outside first; searching outside for resources PathTrove already covers; repeating near-identical searches; opening external pages that have nothing to do with the conclusion. With `PATHTROVE_WEB=off`: no external search, and say that completeness is limited to PathTrove.

## Finding and checking resources

- Learn the fields before filtering: `pathtrove_table_fields` lists the fields with ids, Chinese and English names, kind, and every allowed value with its count. A filter on a misspelled field or value fails with suggestions; a filter that is valid but too narrow returns 0 and tells you how many resources each condition matches alone.
- `pathtrove_table_search` finds candidates: `where` for categorical values, numbers and text (`organ=Lung|Breast`, `image_count>=1000`, `task_description~MSI`), `query` for free words, `fields` to choose the returned columns, `sort`, `offset`/`limit` to page. Start broad and narrow down: a narrow first query drops resources whose records use a different term.
- Counting and comparing is `pathtrove_table_stats` (`group_by` one or two categorical fields, with the same `where`). A resource with several values counts once in each, so group counts can add up to more than the number of resources. Without `group_by` it gives fill rates, which show how complete a field is.
- Read evidence before recommending: `pathtrove_report_get` returns the fields you name for the resources you name; add the text and source layers to see the evidence behind a decision-critical value. Recommend on those values, not on names or search snippets.
- `pathtrove_report_find` locates a literal term in the reports (synonyms and translations are not matched: try both forms).
- Give every candidate the search returns an explicit verdict (fits / does not fit / cannot tell yet) before drawing any overall conclusion. A candidate you have not opened cannot support "none exists" or "cannot be verified": a search rank or snippet does not show whether a resource fits, and the report often holds the very detail you would otherwise call unknown.
- Labels: `pathtrove_label_list` shows which resources and files exist, with each file's split parts and sample counts (filter the files by level, task type, task name, `split` = any / none / train,val,test, and `split_note` = a word such as `patient` searched in the file's split-related text; filter the resources with `where`, the same syntax as `table search`, e.g. `organ=Breast|乳腺`). The index records which parts a file has, not whether the split is by patient, slide or image: that is stated, when at all, only in the file's limitations / task-schema text, which `label list` shows next to the files, so quote it as text; `pathtrove_label_get` gives task, level, class counts, splits and sample counts from the local index, never sample rows. The raw `label.json` files (up to 1.2 GB) are not in the data package (only an index): `pathtrove_label_fetch` downloads one from the public PathTrove repo on Hugging Face into a directory you give and checks its sha256. Check the file size in `label list` and tell the user before fetching a large one.

## Planning a download

- `pathtrove_download_plan` gives the open status, license and links (structured) and, as labelled text, the access conditions and the method. `pathtrove_download_objects` gives what can be downloaded and how big, as text from the guide and the report. `pathtrove_download_guide` gives the guide by section (both guide templates are mapped onto the same section names; without `section` you get the outline).
- The dataset size, the access gate (whether an application or login is needed) and the list of downloadable objects have no structured value in this release. The commands show the text and label it as text. Quote it as text with its source; do not turn it into a number or a yes/no of your own.
- `pathtrove_download_test` is the record of one download test on a date, tested from PathTrove's test environment; the network conditions are those in the recorded note (do not infer where it ran). It is not the dataset size and not a property of the resource: bytes received are what the test downloaded (often a 1 MiB sample), content length is the size of the file(s) the test named, and "direct failed" can mean blocked from there. Never report a test figure as the dataset size or as proof of access.

## Reporting what you found

- Value-only data takes precedence over prose. Where a structured value exists, quote it; where the data has no value, say it is missing (or quote the prose, labelled as prose). Do not fill a missing value from a guess or from another field.
- Quote numbers as the report gives them and name the field they came from. Where the report records conflicting sources, say so; do not pick one silently.
- Decision-critical values (cohort size, label definition, license, access conditions) are the report's values; cite the source the report gives for them. Do not re-check them on the web. The current release declares that field reliability, depth and coverage are still limited; say so when it matters.
- A resource absent from PathTrove may still exist. Say "not found in PathTrove <version>", not "does not exist". If the user needs completeness, follow the external search policy above (or, with `PATHTROVE_WEB=off`, say that completeness is limited to PathTrove).
- PathTrove does not host or redistribute data. Access is governed by each provider's terms; a listing grants no access rights.
