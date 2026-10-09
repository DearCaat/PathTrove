"""Command line and MCP server: `pathtrove <domain> <verb>`.

Domains: table (fields, search, stats), report (get, find), download (plan, objects, test, guide),
label (list, get, fetch), best-data (principles: from a research need to recommended datasets), plus `version` and `data` (install/status of the data package). Every command takes `lang` (zh|en;
default from PATHTROVE_LANG, else zh). The data package is downloaded from Hugging Face on first use and cached (see store.py).
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Callable

from . import best, download, label, report, store, table
from .data import Data
from .errors import PtError
from .i18n import L, norm_lang

SERVER_VERSION = "0.1.0"
PROTOCOL_VERSION = "2025-06-18"

QUICKSTART = """\
Agent quickstart. Every command is read-only; the download domain gives plans and facts and never downloads a dataset.
Results are headed by the data version; cite it. Default output is the value layer only; add --layer text,source (or all).

  pathtrove version                                        data version, usage rules, counts, limitations, translation coverage
  pathtrove table fields                                   the fields: ids, Chinese/English names, allowed values with counts
  pathtrove table search --where 'organ=Lung|Breast' --where 'staining=H&E' --fields organ,image_count --limit 10
  pathtrove table search --query colorectal MSI --sort image_count:desc
  pathtrove table stats --group-by organ --where 'openness=Fully Open'      grouped counts (1-2 fields); no --group-by = fill rates
  pathtrove report get --resource BreakHis --fields 3,16,32 --layer value,source
  pathtrove report find --text 'Visium|Xenium' --fields task_description,data_details
  pathtrove download plan --resource SurGen                how to get it, access conditions, license
  pathtrove download objects --resource SurGen             what can be downloaded and how big (text from the guide)
  pathtrove download test --resource SurGen                the download test record (not a dataset property)
  pathtrove download guide --resource BRACS --section access
  pathtrove label list --level wsi                         resources with WSI-level label files
  pathtrove label list --where 'organ=Breast' --split train,test     breast resources whose label files have official train and test parts (counts shown)
  pathtrove label get --resource ACROBAT                   task, level, classes, splits, counts
  pathtrove label fetch --resource ACROBAT --file acrobat.wsi_registration.label.json --dest ./labels
  pathtrove best-data principles                           from a research need to recommended datasets: method, schema map, outside-search policy

Notes
  fields   by id (1-38), Chinese or English name; resources by PTD id (PTD-000001), name or record id (--resource, repeat or comma-separate).
  filters  --where 'FIELD=A|B'  'FIELD!=A'  'FIELD~term'  'FIELD>=100'  'FIELD:filled'  'FIELD:empty'   (repeat = AND)
  output   --format md|json|ndjson; --output FILE writes a large result to a file and returns only a summary.
  language every command takes --lang zh|en (default: environment variable PATHTROVE_LANG, else zh). Use the language the user writes in.
           Field names, allowed values, notes and errors come in that language; report and guide text is the translation when it exists
           and passed the check, else the original Chinese, and the output says so (lang=zh on that row). Categorical values may be given in either language.
  data     the data package (a versioned archive on Hugging Face) is downloaded and cached on first use: `pathtrove data status`,
           `pathtrove data install --file <archive>` (offline). HF_ENDPOINT selects a mirror; PATHTROVE_HOME the cache directory.
  missing  a value the data does not have stays missing; where only prose exists (dataset size, access gate, object list)
           the text is shown and labelled as text. "Not found in PathTrove" does not mean "does not exist".
"""


@dataclass
class Arg:
    name: str
    help: str
    kind: str = "str"            # str | int | list | choice | json
    choices: tuple[str, ...] = ()
    flags: tuple[str, ...] = ()  # extra spellings
    required: bool = False
    default: Any = None


@dataclass
class Cmd:
    domain: str
    verb: str
    summary: str
    description: str
    args: list[Arg] = field(default_factory=list)
    run: Callable[..., str] | None = None
    common: tuple[str, ...] = ("format", "output", "lang")


RES = Arg("resource", "PTD id (PTD-000001), dataset name or record id; repeat or comma-separate for several", "list",
          flags=("--resources", "--name", "--names", "--id", "--ids"))
LAYER = Arg("layer", "layers to return: value (default), text, source; comma-separated, or all", "str")
LANG = Arg("lang", "language of the output: zh or en (default: PATHTROVE_LANG, else zh). Use the language the user writes in", "choice", ("zh", "en"))
WHERE = Arg("where", "filter, repeatable (AND): FIELD=A|B, FIELD!=A, FIELD~term, FIELD>=N, FIELD:filled, FIELD:empty. Field by id/name (see `table fields`)", "list")
QUERY = Arg("query", "free-text words matched in the name and all text columns", "list", flags=("--q",))
MATCH = Arg("match", "how --query words combine: all (default) or any", "choice", ("all", "any"))
OFFSET = Arg("offset", "skip this many results (paging)", "int")
LIMIT = Arg("limit", "maximum number of results", "int")


def _n(a: dict[str, Any], key: str, default: int) -> int:
    return default if a.get(key) is None else int(a[key])


def _cmds() -> list[Cmd]:
    return [
        Cmd("table", "fields", "field catalogue: ids, names, kinds, allowed values with counts",
            "Lists the fields of the resource table with id, Chinese and English name, kind, how many resources have a value, and for "
            "categorical fields every value with its count. Use it before filtering: a filter on a misspelled value returns nothing.",
            [Arg("field", "show one field only (id or name)"), Arg("values_limit", "values shown per field (default 40)", "int")],
            lambda d, a: table.fields(d, a.get("field"), _n(a, "values_limit", 40), a.get("format"), a.get("output"))),
        Cmd("table", "search", "find resources by categorical filters, numeric ranges, text; projection, sorting, paging",
            "Structured search over the resource table. Returns id (the PTD id), name and the requested fields (--fields; default organ, staining, "
            "task tags, openness). Prose columns are filtered with ~ but not displayed here; use `report get`.",
            [QUERY, MATCH, WHERE, Arg("fields", "columns to return, comma-separated (ids or names)"),
             Arg("sort", "FIELD or FIELD:desc (numeric, date, categorical)"), OFFSET, LIMIT],
            lambda d, a: table.search(d, a.get("query"), a.get("where"), a.get("fields"), a.get("sort"), _n(a, "offset", 0),
                                      _n(a, "limit", 20), a.get("match") or "all", a.get("format"), a.get("output"))),
        Cmd("table", "stats", "grouped counts (one or two categorical fields) or, without --group-by, the overview with fill rates",
            "Counts use the value layer only. A resource with several values counts once in each of them.",
            [Arg("group_by", "one or two categorical fields, comma-separated (e.g. organ or organ,staining)", "str",
                 flags=("--group", "--by")), WHERE, QUERY, MATCH, Arg("top", "groups shown (default 50)", "int")],
            lambda d, a: table.stats(d, a.get("group_by"), a.get("where"), a.get("query"), a.get("match") or "all", _n(a, "top", 50),
                                     a.get("format"), a.get("output"))),
        Cmd("report", "get", "the report fields of resources, in layers value / text / source",
            "Value = the structured block of the field, text = the prose, source = the primary sources it cites. Default: value only; "
            "the output lists which other layers exist. A field with no structured value says so.",
            [RES, Arg("fields", "field ids or names, comma-separated, or all (id and name are always returned)", required=True), LAYER],
            lambda d, a: report.get(d, a.get("resource"), a.get("fields"), a.get("layer"), a.get("format"), a.get("output"))),
        Cmd("report", "find", "locate literal terms inside report fields",
            "Literal, case-insensitive match. By default searches the value and text layers of all fields of all resources.",
            [Arg("text", "TERM or TERM|TERM", required=True, flags=("--term", "--terms")),
             Arg("fields", "restrict to these fields (default all)"), RES, Arg("layer", "layers to search (default value,text)"), LIMIT],
            lambda d, a: report.find(d, a.get("text"), a.get("fields"), a.get("resource"), a.get("layer"),
                                     _n(a, "limit", 30), a.get("format"), a.get("output"))),
        Cmd("download", "plan", "how to obtain a resource: open status, license, links, access conditions",
            "Value: open status, license, download links (table). The access gate and the method have no structured value; their text is "
            "shown and labelled. Plans and facts only; nothing is downloaded.",
            [RES, LAYER], lambda d, a: download.plan(d, a.get("resource"), a.get("layer"), a.get("format"), a.get("output"))),
        Cmd("download", "objects", "downloadable objects and sizes, as text from the guide and the report",
            "The data has no structured object list or dataset size: this shows the guide's download-objects section and the report's "
            "storage-size text, labelled as text.",
            [RES, Arg("layer", "add source to include the sources of the size text")],
            lambda d, a: download.objects(d, a.get("resource"), a.get("layer"), a.get("format"), a.get("output"))),
        Cmd("download", "test", "the download test record: date, status, reachability, bytes received",
            "A record of one download test, tested from PathTrove's test environment on a date; the network conditions are those in the recorded note. It is not the dataset size and not a property of the resource.",
            [RES, Arg("layer", "value (default), text (the notes), source")],
            lambda d, a: download.test(d, a.get("resource"), a.get("layer"), a.get("format"), a.get("output"))),
        Cmd("download", "guide", "the download guide by section (both templates mapped onto one set of section names)",
            "Without --section: the outline. Section names: " + ", ".join(download.SECTION_ORDER) + ", or all.",
            [RES, Arg("section", "section names, comma-separated, or all", "str", flags=("--sections",))],
            lambda d, a: download.guide(d, a.get("resource"), a.get("section"), a.get("format"), a.get("output"))),
        Cmd("label", "list", "resources with label files, or the label files of a resource",
            "Label files map samples to task labels and splits. This lists them; `label get` summarizes one; `label fetch` downloads the raw file.",
            [RES, Arg("level", "label level (patch, wsi, slide, cell, patient, region, roi, ...)"),
             Arg("task_type", "task type (classification, segmentation, detection, survival, ...)", flags=("--task-type",)),
             Arg("task", "substring of the task name"),
             Arg("where", "filter the resources, same syntax as `table search --where` (repeatable, AND): e.g. 'organ=Breast|乳腺', "
                          "'staining=H&E', 'openness=Fully Open', 'license~CC-BY'. Values may be given in either language", "list"),
             Arg("split", "official split of the file: any (has one), none (has none), or the parts it must have, comma-separated: "
                          "train, val, test (e.g. train,test). The split unit (patient / slide / image) is not a field: see split_note"),
             Arg("split_note", "substring (e.g. patient) searched in the file's split-related text (limitations and task-schema split "
                               "entries), the only place where the split unit is stated", flags=("--split-note",)),
             OFFSET, LIMIT],
            lambda d, a: label.list_(d, a.get("resource"), a.get("level"), a.get("task_type"), a.get("task"), _n(a, "offset", 0),
                                     _n(a, "limit", 30), a.get("format"), a.get("output"), a.get("where"), a.get("split"),
                                     a.get("split_note"))),
        Cmd("label", "get", "task, level, classes, splits and counts of a resource's label files",
            "Summaries from the bundled label index; never sample rows.",
            [RES, Arg("file", "substring of the label file name"), Arg("level", "filter by level"),
             Arg("task_type", "filter by task type", flags=("--task-type",)), Arg("task", "substring of the task name"),
             Arg("split", "only files that have this split (any, none, or parts such as train,test), and show only those parts"), LAYER,
             Arg("max_classes", "classes shown per file (default 30)", "int", flags=("--max-classes",))],
            lambda d, a: label.get(d, a.get("resource"), a.get("file"), a.get("level"), a.get("task_type"), a.get("task"), a.get("split"),
                                   a.get("layer"), _n(a, "max_classes", 30), a.get("format"), a.get("output"))),
        Cmd("label", "fetch", "download one raw label.json from the public Hugging Face repo and verify its sha256",
            "The data package holds an index only. Files can be large (up to 1.2 GB); check the size in `label list` first. Needs network access to huggingface.co (or HF_ENDPOINT).",
            [RES, Arg("file", "label file name (needed if the resource has several)"), Arg("dest", "target directory", required=True)],
            lambda d, a: label.fetch(d, a.get("resource"), a.get("dest"), a.get("file")), common=("lang",)),
        Cmd("best-data", "principles", "from a research need to recommended datasets: the method, a map of the schema, the outside-search policy",
            "No plan and no review: read the principles, then do the work with `table` and `report`. Returns five principles (analyse the need; turn hard conditions "
            "into filters; start broad and re-check conditions on an empty pool; judge on report evidence and respect k; outside search for coverage gaps only) "
            "and, from the installed data, which columns can filter, which hold prose only and which fields exist only in the report.",
            [], lambda d, a: best.principles(d, a.get("format"), a.get("output"))),
    ]


CMDS = _cmds()
BY_NAME = {(c.domain, c.verb): c for c in CMDS}



KNOWN_STRUCTURED_GAPS = {
    "en": [
        "dataset total size: only prose (report field 15 / guide tables); no structured value",
        "access gate (whether an application or login is needed): only prose (report field 4); no structured value",
        "list of downloadable objects with sizes: only the guide's table text; no structured list",
        "(listed for the next data version; commands show the text and label it as text)",
    ],
    "zh": [
        "数据集总大小：只有文字（报告字段 15 / 指南表格），没有结构化取值",
        "访问门槛（是否需要申请或登录）：只有文字（报告字段 4），没有结构化取值",
        "可下载对象及大小清单：只有指南表格里的文字，没有结构化清单",
        "（列入下一版数据的改进清单；命令会给出这些文字，并标明它们是文字）",
    ],
}

USAGE_RULES = {
    "en": [
        "1. Cite data_version in every answer built on PathTrove.",
        "2. Give every candidate a search returns an explicit verdict (fits / does not fit / cannot tell yet); open the report before judging.",
        "3. 'Not found in PathTrove' is not 'does not exist'. If the need asks for completeness, or PathTrove returns too few or none, say so and follow the external-search policy (below).",
        "4. Stay with the value layer. If a value is missing, say only text exists (or nothing); never fill it from a guess or another field.",
        "5. The download test record is one test on one date, not a property of the dataset; bytes received or content length are not the dataset size.",
        "6. Decision-critical values (cohort size, labels, license, access) come from the report's value layer; read the text and source layers (`--layer text,source`) for the evidence behind them. Do not re-check them on the web: the curated record is the evidence.",
        "7. If a PathTrove call fails, report the error; do not silently substitute web search for it.",
        "8. Answer in the language the user writes in and pass lang=zh|en accordingly on every call, so the output never mixes languages; run `table fields` before filtering.",
        "9. To recommend datasets for a research need, call `best-data principles` and follow it: analyse the need, turn hard conditions into filters, start broad, judge on report evidence, respect k. There is no plan or review step; you work with `table` and `report`.",
        "10. External search follows the policy below; `PATHTROVE_WEB` (shown in `version`) says whether it is on.",
        "11. Write the answer for the user, not for the tools: do not quote internal names such as field ids, rule or principle numbers, tool or command names, or environment variables (PATHTROVE_WEB); say in plain words what they mean (for example \"external search was off\", \"the table has no structured value for race\").",
        "12. Resources are identified by their PTD id (for example PTD-000123, the id column of every table and label result); cite it with data_version. A name or record id also works as input.",
    ],
    "zh": [
        "1. 凡基于 PathTrove 的回答都要写明 data_version（数据版本）。",
        "2. 对检索返回的每个候选给出明确结论（符合 / 不符合 / 暂无法判断）；判断之前先打开报告。",
        "3.“在 PathTrove 里没找到”不等于“不存在”。需求要求完整性，或 PathTrove 结果太少、没有时，要说明，并按下面的外部检索策略处理。",
        "4. 以值层为准。某个值缺失时，只说明“只有文字”（或什么都没有）；不得凭猜测或用别的字段补。",
        "5. 下载测试记录是某一天的一次测试，不是数据集的属性；收到的字节数或 content length 不是数据集大小。",
        "6. 决定性的数值（队列规模、标签、许可证、访问方式）以报告的值层为准；背后的证据读文字层和来源层（`--layer text,source`）。不要再到网上复核：策展记录本身就是证据。",
        "7. PathTrove 调用失败时如实报告错误，不要悄悄改用网络搜索来代替。",
        "8. 用用户书写的语言回答，并在每次调用里传对应的 lang=zh|en，保证输出不混用语言；过滤之前先运行 `table fields`。",
        "9. 为研究需求推荐数据集时，先调用 `best-data principles` 并照它做：分析需求、把硬条件落成过滤、先宽后窄、在报告证据上判断、遵守 k。没有计划或审查环节；你用 `table` 和 `report` 完成。",
        "10. 外部检索遵循下面的策略；`PATHTROVE_WEB`（见 `version`）说明它是否开启。",
        "11. 回答是写给用户的，不是写给工具的：不要引用内部名称，如字段编号、规则或原则编号、工具或命令名、环境变量（PATHTROVE_WEB）；用平实的话说出它的意思（例如“本次没有做外部检索”“表里没有种族的结构化取值”）。",
        "12. 每个资源都有永久编号 PTD（如 PTD-000123），即每个表格与标签结果中的 id 列；引用资源时连同 data_version 一起给出。名称或 record id 仍可用于输入。",
    ],
}

WEB_POLICY = best.WEB_POLICY


def version_info(d: Data) -> str:
    lang = d.lang
    m = d.manifest
    tr = m.get("translations") or {}
    lab = m.get("labels") or {}
    lim = m.get("known_limitations_zh") if lang == "zh" and m.get("known_limitations_zh") else m.get("known_limitations")
    st = store.status(m)
    info = {"data_version": m["data_version"], "command": "version", "lang": lang, "released": m.get("released"), "counts": m.get("counts"),
            "usage_rules": USAGE_RULES[lang],
            "external_search": {"PATHTROVE_WEB": "on" if best.web_enabled() else "off",
                                "policy": [x.replace("<data_version>", m["data_version"]) for x in WEB_POLICY[lang]]},
            "best_data": {"principles": best.heads(lang),
                          "details": L(lang, "`pathtrove best-data principles` (MCP: pathtrove_best_data_principles) gives the full text and a schema map",
                                       "`pathtrove best-data principles`（MCP：pathtrove_best_data_principles）给出全文和 schema 地图")},
            "known_limitations": lim,
            "structured_values_missing": KNOWN_STRUCTURED_GAPS[lang],
            "english": {"reports": tr.get("reports"), "guides": tr.get("guides"),
                        "note": L(lang, tr.get("note", "no English translations in the data package"),
                                  "只有通过机械检查的英文译文才收入数据包；其余资源在 lang=en 时回退为中文原文，并在输出里标明")},
            "language": {"call_lang": lang, "default": "PATHTROVE_LANG, else zh",
                         "note": L(lang, "pass lang=zh|en in the language the user writes in; the table is available in both languages",
                                   "按用户书写的语言传 lang=zh|en；表格有中英两种语言")},
            "data_package": {"installed": st["installed"], "location": st["location"], "hf_endpoint": st["hf_endpoint"],
                             "archive_url": st["archive"]["url"]},
            "label_files": {"hosted_at": f"https://huggingface.co/datasets/{lab.get('hf_repo', '')}",
                            "count": lab.get("count"), "total_bytes": lab.get("total_bytes"),
                            "note": L(lang, "the data package holds a label index only; `label fetch` downloads a raw file",
                                      "数据包只含标签索引；`label fetch` 才会下载原始文件")},
            "citation": m.get("citation"), "plugin_cli": SERVER_VERSION}
    return json.dumps(info, ensure_ascii=False, indent=1) + "\n"


# ---------------------------------------------------------------- argparse

def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="pathtrove", description="PathTrove: computational-pathology resources, read locally.",
                                   epilog=QUICKSTART, formatter_class=argparse.RawDescriptionHelpFormatter)
    dom = root.add_subparsers(dest="domain", metavar="<domain>")
    vp = dom.add_parser("version", help="data version, usage rules, counts, limitations, translation coverage")
    vp.add_argument("--lang", choices=("zh", "en"), default=None, help="language of the output (default: PATHTROVE_LANG, else zh)")
    dom.add_parser("mcp", help="run as an MCP server on stdio")
    dp = dom.add_parser("data", help="the data package: status, install from a local archive")
    dv = dp.add_subparsers(dest="verb", metavar="<verb>")
    for name, hp in (("status", "where the data package is and whether it is installed"),
                     ("install", "download the data package now, or install it from a local archive (--file)")):
        p = dv.add_parser(name, help=hp)
        p.add_argument("--lang", choices=("zh", "en"), default=None)
        if name == "install":
            p.add_argument("--file", default=None, help="a local copy of the archive (offline install); it is verified against the plugin manifest")
    domains: dict[str, Any] = {}
    for c in CMDS:
        if c.domain not in domains:
            p = dom.add_parser(c.domain, help={"table": "resource table: fields, search, stats", "report": "resource reports: get, find",
                                               "download": "how to obtain a resource: plan, objects, test, guide",
                                               "label": "label files: list, get, fetch",
                                               "best-data": "from a research need to recommended datasets: principles"}[c.domain],
                               epilog=QUICKSTART, formatter_class=argparse.RawDescriptionHelpFormatter)
            domains[c.domain] = p.add_subparsers(dest="verb", metavar="<verb>")
        sp = domains[c.domain].add_parser(c.verb, help=c.summary, description=c.summary + "\n\n" + c.description, epilog=QUICKSTART,
                                          formatter_class=argparse.RawDescriptionHelpFormatter)
        for a in c.args:
            flags = (f"--{a.name.replace('_', '-')}", *a.flags)
            kw: dict[str, Any] = {"dest": a.name, "help": a.help, "required": a.required}
            if a.kind == "int":
                kw["type"] = int
            elif a.kind == "list":
                kw["action"] = "append"
                if a.name == "query":
                    kw["nargs"] = "+"
            elif a.kind == "choice":
                kw["choices"] = a.choices
            sp.add_argument(*flags, **kw)
        if "format" in c.common:
            sp.add_argument("--format", choices=("md", "json", "ndjson"), default=None, help="md (default), json, or ndjson")
            sp.add_argument("--output", default=None, help="write the full result to this file; return only a summary")
        if "lang" in c.common:
            sp.add_argument("--lang", choices=LANG.choices, default=None, help=LANG.help)
    return root


def flatten(v: Any) -> Any:
    if isinstance(v, list) and v and isinstance(v[0], list):
        return [x for sub in v for x in sub]
    return v


def data_command(verb: str | None, args: dict[str, Any]) -> str:
    lang = norm_lang(args.get("lang"))
    m = store.plugin_manifest()
    if verb == "install":
        st = store.install_file(args["file"], lang) if args.get("file") else None
        if st is None:
            store.ensure_data(lang)
            st = store.status(m)
    elif verb == "status":
        st = store.status(m)
    else:
        raise PtError(L(lang, "data commands: status, install [--file ARCHIVE]", "data 命令：status、install [--file 压缩包]"))
    return json.dumps(st, ensure_ascii=False, indent=1) + "\n"


def execute(domain: str, verb: str | None, args: dict[str, Any]) -> str:
    """Run one command with already-parsed arguments (used by the CLI and the MCP server)."""
    lang = norm_lang(args.get("lang"))
    if domain == "data":
        return data_command(verb, args)
    if domain == "version":
        return version_info(Data(lang))
    cmd = BY_NAME.get((domain, verb))
    if cmd is None:
        raise PtError(L(lang, f"unknown command {domain} {verb}; available: version, ", f"未知命令 {domain} {verb}；可用：version、")
                      + ", ".join(f"{c.domain} {c.verb}" for c in CMDS))
    allowed = {a.name for a in cmd.args} | set(cmd.common)
    unknown = [k for k, v in args.items() if k not in allowed and v not in (None, "", [])]
    if unknown:
        raise PtError(L(lang, f"{domain} {verb} has no parameter {unknown}; parameters: {sorted(allowed)}",
                        f"{domain} {verb} 没有参数 {unknown}；可用参数：{sorted(allowed)}"))
    for a in cmd.args:
        if a.required and args.get(a.name) in (None, "", []):
            raise PtError(L(lang, f"{domain} {verb} needs {a.name}: {a.help}", f"{domain} {verb} 需要参数 {a.name}：{a.help}"))
    clean = {k: flatten(v) for k, v in args.items() if v not in (None, "", [])}
    return cmd.run(Data(lang), clean)


def main(argv: list[str]) -> int:
    parser = build_parser()
    ns = parser.parse_args(argv)
    if not ns.domain:
        parser.print_help()
        return 0
    if ns.domain == "mcp":
        serve_mcp()
        return 0
    if ns.domain not in ("version",) and not getattr(ns, "verb", None):
        parser.parse_args([ns.domain, "--help"])
    args = {k: v for k, v in vars(ns).items() if k not in ("domain", "verb")}
    try:
        sys.stdout.write(execute(ns.domain, getattr(ns, "verb", None), args))
    except PtError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    return 0


# ---------------------------------------------------------------- MCP

def _schema(a: Arg) -> dict[str, Any]:
    if a.kind == "int":
        return {"type": "integer", "description": a.help}
    if a.kind == "list" and a.name == "resource":
        return {"type": "string", "description": a.help}
    if a.kind == "list":
        return {"type": "array", "items": {"type": "string"}, "description": a.help}
    if a.kind == "choice":
        return {"type": "string", "enum": list(a.choices), "description": a.help}
    if a.kind == "json":
        return {"type": "object", "description": a.help}
    return {"type": "string", "description": a.help}


POINTER = " Follow the server instructions (usage rules); pass `lang` = the language the user writes in."

TOOL_TEXT = {
    ("table", "fields"): "Field catalogue of the PathTrove resource table: ids, Chinese and English names, kinds, and every allowed value with its count. Call it before filtering; use ids or names from it in the other commands.",
    ("table", "search"): "Search resources by categorical filters, numeric ranges and text; choose the returned fields (`fields`), sort, page (`offset`/`limit`). `where` entries look like 'organ=Lung|Breast', 'image_count>=1000', 'task_tags~segmentation', 'license:filled'. Returns id, name and the requested fields.",
    ("table", "stats"): "Grouped counts of resources on one or two categorical fields (`group_by`), optionally filtered (`where`, `query`); without `group_by`, the overview: total resources and the fill rate of each field. Counts use the value layer only.",
    ("report", "get"): "Report fields of one or more resources in layers: value (structured), text (prose), source (primary sources cited). Default is value only; the result says which other layers exist. `fields`: ids, Chinese or English names, or 'all'. Report text is the English translation for lang=en when one exists, else the Chinese original (labelled).",
    ("report", "find"): "Find literal terms (TERM|TERM) inside report fields across all resources or the given ones; returns resource, field, layer and a snippet. Default layers: value, text.",
    ("download", "plan"): "How to obtain a resource: open status, license and download links (structured), plus the access-gate and method text (labelled as text: no structured value exists). Plans and facts only; nothing is downloaded.",
    ("download", "objects"): "Downloadable objects and sizes of a resource, as text: the guide's download-objects section and the report's storage-size text, labelled as text (no structured list or dataset size exists).",
    ("download", "test"): "The download test record of a resource: date, method status, direct/proxy reachability, bytes received, file URLs. It records one test from PathTrove's test environment on a date (network conditions as in the recorded note); it is NOT the dataset size and NOT a property of the resource.",
    ("download", "guide"): "The download guide of a resource by section; the two guide templates are mapped onto one set of section names. Without `section` it returns the outline; `section: 'all'` returns everything.",
    ("label", "list"): "Which resources have label files, or with `resource`, the label files of that resource; every file row shows its split parts and sample counts. Filter the files by `level`, `task_type`, `task`, `split` (any / none / train,val,test: official split parts the file must have) and `split_note` (text search, e.g. 'patient', in the file's split-related text: the split unit is stated only there). Filter the resources with `where`, same syntax as `table search` (e.g. ['organ=Breast|乳腺', 'staining=H&E']). Label files map samples to task labels and splits.",
    ("label", "get"): "Task, level, class counts, splits and sample counts of a resource's label files, from the bundled index (never sample rows). `layer` text/source adds the task schema, limitations and provenance.",
    ("best-data", "principles"): "From a research need to recommended datasets. Call it when the user describes a research need and wants datasets recommended. There is no plan, review or receipt: it returns five principles (analyse the need and mark hard conditions; turn them into filters on the schema, by field, value and layer; start broad and re-check the conditions once against the user's words when the pool is empty or very small; judge on report evidence, respect k, counts agree with the list; outside search only for coverage gaps) and a schema map of this data version. You then work with `table` and `report`.",
    ("label", "fetch"): "Download one raw label.json of a resource from the public Hugging Face repo to `dest` and verify its sha256 against the data manifest. Files can be large (up to 1.2 GB): check the size with `label list` first. `file` is required when the resource has several.",
}

LANG_PROP = {"type": "string", "enum": ["zh", "en"],
             "description": "language of the output: zh or en (default PATHTROVE_LANG, else zh). Use the language the user writes in"}


def instructions() -> str:
    text = ("PathTrove: a curated, versioned database of computational-pathology resources (table, reports, download guides, label index), "
            "read read-only from a local data package. Call `pathtrove_version` first; it returns the data version and these rules in the "
            "language you pass as `lang`.\n\nUsage rules:\n" + "\n".join(USAGE_RULES["en"])
            + "\n\nEvery tool takes `lang` (zh|en). Set it to the language the user writes in on every call; do not mix languages in the answer. "
              "The data package is downloaded from Hugging Face on first use; if a call reports that it is missing, relay the fix in the error."
            + f"\n\nExternal search policy (PATHTROVE_WEB={'on' if best.web_enabled() else 'off'}):\n" + "\n".join("- " + x for x in WEB_POLICY["en"]))
    text += "\n\nRecommending datasets for a research need (`pathtrove_best_data_principles` gives the full text and a schema map):\n" + "\n".join(best.heads("en"))
    return text


def tools() -> list[dict[str, Any]]:
    out = [{"name": "pathtrove_version", "description": "Data version, release date, counts, usage rules, known limitations and translation coverage of the PathTrove release. Call once per task; cite the version in the answer." + POINTER,
            "inputSchema": {"type": "object", "properties": {"lang": LANG_PROP}, "required": []}}]
    for c in CMDS:
        props = {a.name: _schema(a) for a in c.args if a.name != "lang"}
        if "format" in c.common:
            props["format"] = {"type": "string", "enum": ["md", "json", "ndjson"], "description": "md (default), json or ndjson"}
            props["output"] = {"type": "string", "description": "write the full result to this file and return only a summary"}
        props["lang"] = LANG_PROP
        out.append({"name": f"pathtrove_{c.domain.replace('-', '_')}_{c.verb}", "description": TOOL_TEXT[(c.domain, c.verb)] + POINTER,
                    "inputSchema": {"type": "object", "properties": props, "required": [a.name for a in c.args if a.required]}})
    return out


def tool_result(text: str, is_error: bool = False) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


def handle(msg: dict[str, Any]) -> dict[str, Any] | None:
    method, mid = msg.get("method"), msg.get("id")
    if mid is None:
        return None
    if method == "initialize":
        result: Any = {"protocolVersion": msg.get("params", {}).get("protocolVersion", PROTOCOL_VERSION),
                       "capabilities": {"tools": {}}, "serverInfo": {"name": "pathtrove", "version": SERVER_VERSION},
                       "instructions": instructions()}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": tools()}
    elif method == "tools/call":
        params = msg.get("params", {})
        name = str(params.get("name", "")).removeprefix("pathtrove_")
        args = {k: v for k, v in (params.get("arguments") or {}).items() if v not in (None, "", [])}
        try:
            if name == "version":
                result = tool_result(execute("version", None, args))
            else:
                if name.startswith("best_data_"):
                    domain, verb = "best-data", name[len("best_data_"):]
                else:
                    domain, _, verb = name.partition("_")
                result = tool_result(execute(domain, verb, args))
        except PtError as err:
            result = tool_result(f"error: {err}", True)
        except Exception as err:                       # a bug must not kill the server
            result = tool_result(f"internal error: {type(err).__name__}: {err}", True)
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"unknown method {method}"}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def serve_mcp() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        reply = handle(json.loads(line))
        if reply is not None:
            sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            sys.stdout.flush()
