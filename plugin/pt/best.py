"""best-data domain: principles for going from a research need to recommended datasets.

There is no plan, no review and no state here. `best-data principles` returns what an agent needs to do the work with the other domains
(`table fields` / `table search` / `table stats`, `report get` / `report find`): five short principles, each with its reason, a map of the
schema (which column is a table filter, which text is prose only, which fields exist only in the report) generated from the installed data,
and the external-search policy. Nothing is executed on the data and nothing is stored.
"""
from __future__ import annotations

import os
from typing import Any

from .data import Data
from .i18n import L
from .render import emit
from .table import derived_columns, kind_name, observed_values


def web_enabled() -> bool:
    """PATHTROVE_WEB=on|off (default on): whether the agent may search outside PathTrove. The plugin cannot switch a client's web tools; it states the setting."""
    return os.environ.get("PATHTROVE_WEB", "on").strip().lower() not in ("off", "0", "false", "no")


# Each principle: (id, one-line head, points with their reasons). Heads go into the server instructions and `version`; the full text is `best-data principles`.
PRINCIPLES = {
    "en": [
        ("need", "Analyse the need: write each condition in the user's words and mark it hard (one structured value expresses it directly and stably) or to be judged on the report evidence.",
         ["A table filter can only cut on what the table records, so only a condition that one value expresses directly and stably is a filter. A condition that is a matter of degree, a concept, a quality or a method is judged on reports.",
          "If the user lists the hard conditions, only those are filters; the rest of the need is judged on the candidates.",
          "Keep the user's wording for every condition. You will compare the filters against it later."]),
        ("filters", "Turn hard conditions into filters on the schema: pick the field, the value and the layer; if no structured column holds the condition, recall candidates from the report and judge them there.",
         ["Run `table fields` first: it lists columns, kinds, allowed values with counts, and `filled` (resources with a value). A column with `filled` near 0 cannot filter anything.",
          "Table layer: `table search --where 'col=a|b'` (any of a, b); repeated `--where` are ANDed; alternatives across different columns are separate searches whose results you merge. Use exact values from `table fields`; kinds and operators are in its output.",
          "Report layers: value (structured block), text (prose), source (primary sources). Some structured details live only in a report's value layer and have no table column; some fields exist only in the report. `report find` searches the value and text layers for literal words.",
          "A condition with no structured column: recall with `report find` (or `~` on a prose column), then judge on the reports. These searches match literal words only: try the Chinese and English forms and synonyms. A hit is a candidate to read, a miss is not evidence of absence.",
          "Prose-only columns carry no structured value; filter them with `~` and read them with `report get --layer text`."]),
        ("broad", "Start broad, and when the pool is empty or very small go back to the conditions once, against the user's own words.",
         ["Begin with the fewest filters you are sure of and read the counts (`table search` shows the total; `table stats` shows the distribution). Add a filter only when the pool is too large to judge.",
          "A pool of 0 or very few is a signal, not a result. Re-read the user's words once and check each filter: does it stand for a condition that should be judged, not filtered; is a value too wide or too narrow; is AND used where the user meant OR (or the reverse); is the value in the column at all (`table fields`).",
          "Change only the filter that is wrong and run again. If the pool is still empty, say so: none in PathTrove <data_version>, and which condition cut it. Do not loosen a condition silently to get something to show."]),
        ("judge", "Judge on the report: open it before judging; \"fits\" only on evidence you read there (name the field), otherwise \"cannot tell yet\"; respect k; counts agree with the list.",
         ["Verdict per candidate: fits / does not fit / cannot tell yet. \"Fits\" needs evidence read in the report for every condition, with the field named; if a condition is not covered, the verdict is \"cannot tell yet\" and you say what is missing. Existence of a dataset is not availability; a subset can fit when the whole does not.",
          "Respect the number k: show at most k that fit, no padding with ones that do not; put near misses in a separate list labelled as such; if fewer than k fit, say so and why. If the user gave no number, do not invent one.",
          "The counts you state (pool size, opened, fits) must agree with the list you give. If you opened only part of the pool, say \"N of M\".",
          "The user's requested form comes first; answer in the user's language; cite the data version."]),
        ("outside", "Outside PathTrove: external search fills coverage gaps only.",
         ["See the external search policy below."]),
    ],
    "zh": [
        ("need", "分析需求：把每个条件按用户原话写下来，标出哪些是硬条件（一个结构化取值就能直接、稳定地表达），哪些要在报告证据上判断。",
         ["表的过滤只能按表里记录的内容切，所以只有一个取值就能直接、稳定表达的条件才是过滤条件；程度、概念、质量、方法一类的条件要在报告上判断。",
          "用户若列出了硬条件，只有这些是过滤条件；需求的其余部分在候选上判断。",
          "每个条件都保留用户的原话，之后要拿过滤条件去对照它。"]),
        ("filters", "把硬条件落成 schema 上的过滤：选字段、取值和层；没有结构化列承载的条件，从报告里召回候选并在报告上判断。",
         ["先运行 `table fields`：它列出各列、类型、允许取值及计数，以及 `filled`（有值的资源数）。`filled` 接近 0 的列什么也过滤不了。",
          "表层：`table search --where 'col=a|b'`（a、b 任一）；重复的 `--where` 是 AND；跨不同列的备选条件要分开检索再合并结果。取值用 `table fields` 里的原值；类型与运算符见其输出。",
          "报告层：value（结构化块）、text（文字）、source（来源）。有些结构化细节只在报告的 value 层里，没有表列；有些字段只存在于报告。`report find` 在 value 层和 text 层里按字面词检索。",
          "没有结构化列的条件：用 `report find`（或对文字列用 `~`）召回，再在报告上判断。这类检索只匹配字面词：中英文写法和同义词都要试。命中是要去读的候选，没命中不是“没有”的证据。",
          "只有文字的列没有结构化取值；用 `~` 过滤，用 `report get --layer text` 阅读。"]),
        ("broad", "先宽后窄；池为空或很小时，回到条件上，对照用户原话核对一次。",
         ["从最少的、有把握的过滤开始，读数量（`table search` 给总数；`table stats` 给分布）。只有池大到判断不过来时才加过滤。",
          "池为 0 或很少是信号，不是结果。重读一遍用户原话，逐个核对过滤：是不是把该判断的条件当成了过滤；取值是不是过宽或过窄；AND 与 OR 有没有用反；该取值在这一列里到底有没有（`table fields`）。",
          "只改有问题的那个过滤，再跑一次。仍然为空就如实说：PathTrove <data_version> 中没有，并说明是哪个条件切空的。不要为了有东西可展示而悄悄放宽条件。"]),
        ("judge", "在报告上判断：先打开报告再判断；“符合”只能基于在报告里读到的证据（写明字段），否则就是“暂无法判断”；遵守数量 k；数字与清单一致。",
         ["每个候选的结论：符合 / 不符合 / 暂无法判断。“符合”要求每个条件都有在报告里读到的证据并写明字段；有条件没覆盖就是“暂无法判断”，并说明缺什么。数据集存在不等于可获得；整体不符合时子集也可能符合。",
          "遵守数量 k：最多展示 k 个符合的，不拿不符合的凑数；接近但不满足的另列一表并标明；符合的不足 k 个就如实说并说明原因。用户没给数字就不要自己编一个 k。",
          "你写出的数字（池的大小、已打开的、符合的）必须与给出的清单一致；只打开了池的一部分时写“M 个里的 N 个”。",
          "用户要求的形式优先；用用户的语言回答；写明数据版本。"]),
        ("outside", "PathTrove 之外：外部检索只补覆盖缺口。",
         ["见下面的外部检索策略。"]),
    ],
}

# The external-search policy (also shown by `version` and in the server instructions).
WEB_POLICY = {
    "en": [
        "PathTrove first: search PathTrove and settle the candidates before going outside it. External results are a different kind of evidence, and searching outside first lets web results take the place of curated records.",
        "Go outside PathTrove for two things only: (1) to fill coverage gaps: when the need asks for completeness, or PathTrove returns too few or none, look for resources PathTrove does not have; (2) when the user explicitly asks for information from outside PathTrove. Not to re-check values of resources PathTrove already covers: the curated record is the evidence, and 'verifying' it on the web puts web prose in its place at the cost of many calls.",
        "Report external findings separately from PathTrove candidates, each labelled \"not in PathTrove <data_version>, not curated\" with its URL and the access date. Never make up a value PathTrove lacks.",
        "Waste: searching outside first; searching outside for resources PathTrove already covers, or to 'verify' them; repeating searches with near-identical terms; opening external pages that have nothing to do with the conclusion.",
        "PATHTROVE_WEB=off: no external search at all; say that completeness is limited to PathTrove <data_version>.",
    ],
    "zh": [
        "先查 PathTrove：先在 PathTrove 里检索并定下候选，再考虑到外面找。外部结果是另一类证据，先查外面会让网页结果取代策展记录。",
        "只在两种情况下到 PathTrove 之外检索：（1）补覆盖缺口：需求要求完整性，或 PathTrove 结果太少、没有时，找 PathTrove 没有的资源；（2）用户明确要求 PathTrove 之外的信息。不用于复核 PathTrove 已收录资源的取值：策展记录本身就是证据，到网上“核实”会让网页文字取代它，还白耗很多调用。",
        "外部发现与 PathTrove 候选分开写，每条标注“不在 PathTrove <data_version> 中，未经策展”，附 URL 和访问日期。PathTrove 没有的值不得编造。",
        "浪费：先查外面；为 PathTrove 已收录的资源去外面检索或“核实”；用近乎相同的词重复检索；打开与结论无关的外部页面。",
        "PATHTROVE_WEB=off：完全不做外部检索；说明完整性仅限于 PathTrove <data_version>。",
    ],
}


def heads(lang: str) -> list[str]:
    """One line per principle (numbered); used by the server instructions and `version`."""
    return [f"{i}. {head}" for i, (_, head, _) in enumerate(PRINCIPLES[lang], 1)]


def schema_map(data: Data) -> dict[str, Any]:
    """Which columns are table filters, which are prose only, which fields are report-only; generated from the installed data."""
    lang = data.lang
    n = len(data.rows)
    by_field: dict[int, list[Any]] = {}
    for c in data.columns:
        by_field.setdefault(c.field_id, []).append(c)
    filters, prose, report_only = [], [], []
    for fid in data.field_ids:
        cols = by_field.get(fid, [])
        if not cols:
            report_only.append({"field_id": fid, "name": data.field_name(fid, lang)})
            continue
        for c in cols:
            if c.kind == "text":
                filled = sum(1 for r in data.rows if r["fields"].get(c.zh) not in (None, ""))
                prose.append({"column_id": c.id, "name": c.name(lang), "filled": filled, "of": n})
            else:
                item = {"column_id": c.id, "name": c.name(lang), "kind": c.kind, "of": n,
                        "filled": sum(1 for r in data.rows if c.value(r) is not None)}
                if c.kind == "categorical":
                    item["n_values"] = len(observed_values(data, c))
                filters.append(item)
    for d in derived_columns(data):
        item = {"column_id": d.id, "name": d.name(lang), "kind": d.kind, "of": n, "derived": True,
                "filled": sum(1 for r in data.rows if d.value(r) is not None)}
        if d.kind == "categorical":
            item["n_values"] = len(observed_values(data, d))
        filters.append(item)
    return {"filters": filters, "prose_only": prose, "report_only": report_only}


def principles(data: Data, fmt: str | None = None, output: str | None = None) -> str:
    lang = data.lang
    sm = schema_map(data)
    web = "on" if web_enabled() else "off"
    policy = [x.replace("<data_version>", data.version) for x in WEB_POLICY[lang]]
    pr = [{"n": i, "id": pid, "head": head, "points": [x.replace("<data_version>", data.version) for x in pts]}
          for i, (pid, head, pts) in enumerate(PRINCIPLES[lang], 1)]
    intro = L(lang, "From a research need to recommended datasets. There is no plan, review or receipt: you do the work with `table` and `report`. "
                    "Principles 1-4 are the method, the schema map says what each column can and cannot do, principle 5 is the external-search policy.",
              "从研究需求到推荐数据集。没有计划、审查或回执：你用 `table` 和 `report` 完成。原则 1–4 是方法，schema 地图说明每一列能做什么、不能做什么，原则 5 是外部检索策略。")
    env = {"data_version": data.version, "command": "best-data principles", "lang": lang, "intro": intro, "principles": pr,
           "schema_map": sm, "external_search": {"PATHTROVE_WEB": web, "policy": policy}}
    body = [intro, ""]
    for p in pr:
        body.append(f"## {p['n']}. {p['head']}")
        body += [f"- {x}" for x in p["points"]]
        body.append("")
    body.append(L(lang, "## Schema map (this data version)", "## Schema 地图（本数据版本）"))
    body.append(L(lang, "Table columns that can filter (allowed values: `table fields`; `filled` = resources with a value; the kind decides the operators):",
                  "可过滤的表列（允许取值见 `table fields`；`filled` = 有值的资源数；运算符由类型决定）："))
    for c in sm["filters"]:
        extra = [kind_name(c["kind"], lang)]
        if c.get("n_values") is not None:
            extra.append(L(lang, f"{c['n_values']} values", f"{c['n_values']} 个取值"))
        extra.append(f"{c['filled']}/{c['of']}")
        if c.get("derived"):
            extra.append(L(lang, "derived from label index", "由标签索引派生"))
        body.append(f"- {c['column_id']} {c['name']} ({', '.join(extra)})")
    body += ["", L(lang, "Prose-only columns (no structured value; `~` filters them, `report get --layer text` reads them):",
                  "只有文字的列（没有结构化取值；`~` 可过滤，`report get --layer text` 阅读）：")]
    body += [f"- {c['column_id']} {c['name']} ({c['filled']}/{c['of']})" for c in sm["prose_only"]]
    body += ["", L(lang, "Report-only fields (no table column; `report get` reads them, `report find` searches them):",
                  "仅报告字段（没有表列；`report get` 阅读，`report find` 检索）：")]
    body.append(", ".join(f"{f['field_id']} {f['name']}" for f in sm["report_only"]) or L(lang, "(none)", "（无）"))
    body += ["", L(lang, f"## 5. External search (PATHTROVE_WEB={web})", f"## 5. 外部检索（PATHTROVE_WEB={web}）")]
    body += [f"- {x}" for x in policy]
    return emit(env, fmt, output, body, None)
