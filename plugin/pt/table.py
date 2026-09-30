"""table domain: field catalogue, search and grouped counts on the structured values of the resource table."""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

from .data import Column, Data, norm, suggest
from .errors import PtError
from .i18n import L
from .render import emit, md_table

DEFAULT_COLUMNS = ["6-1", "7-1", "23-1", "3-1"]
MAX_LIMIT = 200
OPERATORS = {
    "en": {
        "=": "equals any of the |-separated values (categorical, numeric, short text), case-insensitive",
        "!=": "equals none of the values",
        "~": "contains any of the |-separated terms (any column with text, also prose columns), case-insensitive",
        ">=, <=, >, <": "numeric or date comparison (dates compare as YYYY[-MM] text)",
        ":filled / :empty": "the column has / has no value",
    },
    "zh": {
        "=": "等于用 | 分隔的任一取值（分类、数值、短文本），不分大小写",
        "!=": "不等于任何一个取值",
        "~": "包含用 | 分隔的任一词（任何有文本的列，含长文本列），不分大小写",
        ">=, <=, >, <": "数值或日期比较（日期按 YYYY[-MM] 文本比较）",
        ":filled / :empty": "该列有值 / 无值",
    },
}
KIND_HELP = {
    "en": {
        "categorical": "one or more values from a list (multi-valued: a resource can have several)",
        "numeric": "a number", "date": "YYYY or YYYY-MM", "link": "one or more URLs",
        "short": "a short string (name, delimited list); filter with ~ or =",
        "text": "prose only: no structured value. Filter with ~; read it with `report get --layer text`",
    },
    "zh": {
        "categorical": "取自列表的一个或多个值（多值：一个资源可有几个）",
        "numeric": "数值", "date": "YYYY 或 YYYY-MM", "link": "一个或多个链接",
        "short": "短字符串（名称、分隔的列表）；用 ~ 或 = 过滤",
        "text": "只有长文本，没有结构化取值。用 ~ 过滤；用 `report get --layer text` 阅读",
    },
}
KIND_NAME_ZH = {"categorical": "分类", "numeric": "数值", "date": "日期", "link": "链接", "short": "短文本", "text": "长文本"}


def kind_name(kind: str, lang: str) -> str:
    return KIND_NAME_ZH.get(kind, kind) if lang == "zh" else kind


class Derived:
    """A column computed from the label index (not a column of the Feishu table)."""
    field_id = None
    declared = None
    enum: list[str] = []
    is_value = True

    def __init__(self, id_: str, zh: str, en: str, kind: str, getter):
        self.id, self.zh, self.en, self.kind, self._get = id_, zh, en, kind, getter
        self.field_zh, self.field_en = zh, en

    def name(self, lang: str) -> str:
        return self.en if lang == "en" else self.zh

    def label(self, lang: str = "en") -> str:
        return f"{self.id} {self.name(lang)}"

    def value(self, row: dict[str, Any]) -> Any:
        return self._get(row)


def derived_columns(data: Data) -> list[Derived]:
    labels = data.labels_by_resource

    def uniq(key: str):
        return lambda row: sorted({str(r[key]) for r in labels.get(row["id"], []) if r.get(key)}) or None
    return [
        Derived("L1", "标签文件数", "label_files", "numeric", lambda row: len(labels[row["id"]]) if row["id"] in labels else None),
        Derived("L2", "标签层级", "label_level", "categorical", uniq("level")),
        Derived("L3", "标签任务类型", "label_task_type", "categorical", uniq("task_type")),
    ]


def find_column(data: Data, token: str):
    n = norm(token)
    for d in derived_columns(data):
        if n in (norm(d.id), norm(d.en), norm(d.zh)):
            return d
    return data.column(token)


def all_columns(data: Data) -> list[Any]:
    return [c for c in data.columns] + derived_columns(data)


def observed_values(data: Data, col: Any) -> Counter:
    key = ("obs", col.id, data.lang)
    cache = data.__dict__.setdefault("_cache", {})
    if key not in cache:
        c: Counter = Counter()
        for r in data.rows:
            for v in col.value(r) or []:
                c[v] += 1
        cache[key] = c
    return cache[key]


# ---------------------------------------------------------------- filters

class Cond:
    def __init__(self, col: Any, op: str, raw: str):
        self.col, self.op, self.raw = col, op, raw
        self.values = [v.strip() for v in raw.split("|") if v.strip()]

    def text(self, lang: str = "en") -> str:
        return f"{self.col.name(lang)}{self.op}{self.raw}"

    def matches(self, row: dict[str, Any], data: Data) -> bool:
        col, op = self.col, self.op
        val = col.value(row) if not isinstance(col, Column) or col.kind != "text" else row["fields"].get(col.zh)
        if op == ":filled":
            return val not in (None, [], "")
        if op == ":empty":
            return val in (None, [], "")
        if op == "~":
            hay = val if isinstance(val, list) else [val]
            hay = [str(h).casefold() for h in hay if h not in (None, "")]
            return any(t.casefold() in h for t in self.values for h in hay)
        if col.kind == "numeric" or (col.kind == "date" and op in (">=", "<=", ">", "<")):
            if val is None:
                return False
            try:
                if col.kind == "numeric":
                    x, ys = float(val), [float(v) for v in self.values]
                else:
                    x, ys = str(val), [str(v) for v in self.values]
            except ValueError:
                raise PtError(L(data.lang, f"{col.en} is numeric; {self.raw!r} is not a number",
                                f"{col.zh} 是数值字段；{self.raw!r} 不是数字")) from None
            ok = {"=": lambda y: x == y, "!=": lambda y: x != y, ">=": lambda y: x >= y, "<=": lambda y: x <= y,
                  ">": lambda y: x > y, "<": lambda y: x < y}[op]
            return any(ok(y) for y in ys) if op != "!=" else all(ok(y) for y in ys)
        have = [str(v).casefold() for v in (val if isinstance(val, list) else [val]) if v not in (None, "")]
        want = [v.casefold() for v in self.values]
        hit = any(h == w for h in have for w in want)
        if op == "=":
            return hit
        if op == "!=":
            return not hit
        raise PtError(L(data.lang, f"operator {op} does not apply to {col.en} ({col.kind})", f"运算符 {op} 不适用于 {col.zh}（{kind_name(col.kind, 'zh')}）"))


COND = re.compile(r"^(.+?)(:filled|:empty|!=|>=|<=|=|>|<|~)(.*)$")


def parse_where(data: Data, exprs: Any) -> list[Cond]:
    lang = data.lang
    conds = []
    for e in ([exprs] if isinstance(exprs, str) else list(exprs or [])):
        m = COND.match(e.strip())
        if not m:
            raise PtError(L(lang, f"cannot read filter {e!r}. Form: FIELD=VALUE|VALUE, FIELD!=VALUE, FIELD~TERM, FIELD>=NUMBER, "
                                  "FIELD:filled, FIELD:empty. Example: --where 'organ=Lung|Breast' --where 'image_count>=1000'",
                            f"无法解析过滤条件 {e!r}。格式：字段=值|值、字段!=值、字段~词、字段>=数字、字段:filled、字段:empty。"
                            "例：--where '器官=Lung|Breast' --where '有效图像数量>=1000'"))
        field, op, raw = m.group(1).strip(), m.group(2), m.group(3).strip()
        col = find_column(data, field)
        cname = col.name(lang)
        if op not in (":filled", ":empty") and not raw:
            raise PtError(L(lang, f"filter {e!r} has no value", f"过滤条件 {e!r} 没有取值"))
        if op in ("=", "!=") and col.kind == "categorical":
            obs = observed_values(data, col)
            known = {k.casefold(): k for k in obs}
            wanted = [v.strip() for v in raw.split("|") if v.strip()]
            fixed = []
            for v in wanted:                                   # values are accepted in either language
                if v.casefold() in known:
                    fixed.append(known[v.casefold()])
                else:
                    other = data.value_in_lang(col, v)
                    fixed.append(other if other and other.casefold() in known else v)
            unknown = [v for v in fixed if v.casefold() not in known]
            if unknown and len(unknown) == len(fixed):
                near = suggest(unknown[0], list(obs))
                shown = ", ".join(f"{k} ({v})" for k, v in obs.most_common(40))
                more = "" if len(obs) <= 40 else L(lang, f", … {len(obs)} in all; `table fields --field {col.id}` lists them",
                                                   f"，……共 {len(obs)} 个；`table fields --field {col.id}` 可列出全部")
                raise PtError(L(lang,
                                f"{cname} has no value {unknown[0]!r}. " + (f"Did you mean: {', '.join(near)}? " if near else "")
                                + f"Values in {data.version} (count): {shown}{more}. Use ~ for a substring match.",
                                f"{cname} 没有取值 {unknown[0]!r}。" + (f"你是不是想找：{'、'.join(near)}？" if near else "")
                                + f"{data.version} 中的取值（数量）：{shown}{more}。要做子串匹配请用 ~。"))
            raw = "|".join(fixed)
        if op in (">=", "<=", ">", "<") and col.kind not in ("numeric", "date"):
            raise PtError(L(lang, f"{cname} is {col.kind}; comparison operators need a numeric or date field",
                            f"{cname} 是{kind_name(col.kind, 'zh')}字段；比较运算符只适用于数值或日期字段"))
        if col.kind == "text" and op in ("=", "!="):
            raise PtError(L(lang, f"{cname} is prose (text only); use {cname}~TERM to search it",
                            f"{cname} 只有长文本；请用 {cname}~词 来搜索"))
        conds.append(Cond(col, op, raw))
    return conds


def query_hit(data: Data, row: dict[str, Any], words: list[str], mode: str) -> tuple[bool, int]:
    hay = [row["name"].casefold()]
    for c in data.columns:
        v = row["fields"].get(c.zh)
        if isinstance(v, list):
            hay += [str(x).casefold() for x in v]
        elif isinstance(v, str):
            hay.append(v.casefold())
    blob = "\n".join(hay)
    hits = [w.casefold() in blob for w in words]
    ok = all(hits) if mode == "all" else any(hits)
    score = sum(w.casefold() in row["name"].casefold() for w in words) * 2 + sum(hits)
    return ok, score


def filter_rows(data: Data, where: Any, query: Any, match: str = "all") -> tuple[list[dict[str, Any]], list[Cond], dict[str, int]]:
    conds = parse_where(data, where)
    words = [w for q in ([query] if isinstance(query, str) else list(query or [])) for w in str(q).split() if w]
    if match not in ("all", "any"):
        raise PtError(L(data.lang, "--match must be all or any", "--match 只能是 all 或 any"))
    rows = list(data.rows)
    scores: dict[str, int] = {}
    if words:
        keep = []
        for r in rows:
            ok, sc = query_hit(data, r, words, match)
            if ok:
                keep.append(r)
                scores[r["id"]] = sc
        rows = keep
    for c in conds:
        rows = [r for r in rows if c.matches(r, data)]
    return rows, conds, scores


def zero_result_hint(data: Data, conds: list[Cond], query: Any, match: str) -> list[str]:
    lang = data.lang
    notes = [L(lang, "0 resources match.", "没有资源匹配。")]
    if len(conds) + (1 if query else 0) > 1:
        parts = []
        if query:
            parts.append(L(lang, f"query {query}: ", f"查询词 {query}：") + str(len(filter_rows(data, [], query, match)[0])))
        parts += [f"{c.text(lang)}: {sum(1 for r in data.rows if c.matches(r, data))}" for c in conds]
        notes.append(L(lang, "each condition alone matches — " + "; ".join(parts)
                       + ". A narrow first query drops resources whose records use a different term; loosen one condition.",
                       "每个条件单独匹配的数量——" + "；".join(parts) + "。过窄的首个查询会漏掉记录里用了别的说法的资源；请放宽某个条件。"))
    return notes


CJK_CELL = re.compile(r"[㐀-䶿一-鿿]")


def english_only_columns(data: Data) -> dict[str, tuple[int, int]]:
    """{column id: (cells with Chinese, filled cells)} for the text and short columns of the Chinese table whose cells are mostly
    English only (the source table itself has English there; nothing is translated at query time)."""
    cache = data.__dict__.setdefault("_cache", {})
    if "en_only" not in cache:
        out = {}
        for c in data.columns:
            if c.kind not in ("text", "short"):
                continue
            vals = [r["fields"].get(c.zh) for r in data.core.rows]
            vals = [v for v in vals if isinstance(v, str) and v.strip()]
            zh = sum(1 for v in vals if CJK_CELL.search(v))
            if len(vals) >= 20 and zh * 2 < len(vals):
                out[c.id] = (zh, len(vals))
        cache["en_only"] = out
    return cache["en_only"]


def cell(col: Any, row: dict[str, Any], lang: str = "en") -> Any:
    if isinstance(col, Column) and col.kind == "text":
        v = row["fields"].get(col.zh)
        return None if v in (None, "") else (v if len(v) <= 200 else v[:200] + L(
            lang, f"… [{len(v)} chars; text column, read with `report get`]", f"……[共 {len(v)} 字符；长文本列，请用 `report get` 阅读]"))
    return col.value(row)


# ---------------------------------------------------------------- fields

def fields(data: Data, field: str | None = None, values_limit: int = 40, fmt: str | None = None, output: str | None = None) -> str:
    lang = data.lang
    out = []
    is_derived = bool(field) and any(norm(field) in (norm(d.id), norm(d.en), norm(d.zh)) for d in derived_columns(data))
    ids = [] if is_derived else ([data.field_id(field, "table field")] if field else data.field_ids)
    cols_by_field: dict[int, list[Column]] = {}
    for c in data.columns:
        cols_by_field.setdefault(c.field_id, []).append(c)
    for fid in ids:
        cols = cols_by_field.get(fid, [])
        entry = {"field_id": fid, "name_zh": data.field_zh.get(fid), "name_en": data.field_name(fid, "en"), "columns": []}
        for c in cols:
            filled = sum(1 for r in data.rows if c.value(r) is not None) if c.kind != "text" else \
                sum(1 for r in data.rows if r["fields"].get(c.zh) not in (None, ""))
            item: dict[str, Any] = {"column_id": c.id, "name_zh": c.zh, "name_en": c.en, "kind": c.kind, "filled": filled, "of": len(data.rows)}
            if c.kind in ("text", "short"):
                eo = english_only_columns(data).get(c.id)
                if eo:
                    item["text_language"] = f"the Chinese table holds English text in this column ({eo[0]} of {eo[1]} cells contain Chinese)"
            if c.kind == "categorical":
                obs = observed_values(data, c)
                item["n_values"] = len(obs)
                item["values"] = [{"value": k, "count": v} for k, v in obs.most_common(values_limit)]
                if len(obs) > values_limit:
                    item["values_note"] = L(lang, f"{len(obs) - values_limit} more values; raise --values-limit",
                                            f"还有 {len(obs) - values_limit} 个取值；请加大 --values-limit")
                extra = [e for e in c.enum if e not in obs and (data.value_in_lang(c, e) or e) not in obs]
                if extra:
                    item["declared_values_without_resources"] = extra
            entry["columns"].append(item)
        if not cols:
            entry["note"] = L(lang, "report-only field: no column in the table; read it with `report get`",
                              "仅报告字段：表格里没有这一列；请用 `report get` 阅读")
        out.append(entry)
    derived = []
    if not field or is_derived:
        for d in derived_columns(data):
            if field and norm(field) not in (norm(d.id), norm(d.en), norm(d.zh)):
                continue
            item = {"column_id": d.id, "name_en": d.en, "name_zh": d.zh, "kind": d.kind, "source": "derived from label index",
                    "filled": sum(1 for r in data.rows if d.value(r) is not None), "of": len(data.rows)}
            if d.kind == "categorical":
                item["values"] = [{"value": k, "count": v} for k, v in observed_values(data, d).most_common(values_limit)]
            derived.append(item)
    dtag = L(lang, "derived from label index", "由标签索引派生")
    notes = [L(lang, "`filled` counts resources with a value; free-text columns carry prose only (no structured value).",
               "`filled` 是有值的资源数；长文本列只有文字，没有结构化取值。"),
             L(lang, "Derived columns (marked 'derived from label index') come from the label index, not from the source table; "
                     "they can be used in --where, --fields, --group-by.",
               "标注为“由标签索引派生”的列来自标签索引，不是源表的列；可用于 --where、--fields、--group-by。")]
    env = {"data_version": data.version, "command": "table fields", "lang": lang, "notes": notes, "kinds": KIND_HELP[lang],
           "operators": OPERATORS[lang], "fields": out, "derived_columns": derived}
    body = [L(lang, "Kinds: ", "类型：") + L(lang, "; ", "；").join(f"{kind_name(k, lang)} = {v}" for k, v in KIND_HELP[lang].items()), "",
            L(lang, "Filter operators (--where): ", "过滤运算符（--where）：") + L(lang, "; ", "；").join(f"`{k}` {v}" for k, v in OPERATORS[lang].items()), ""]
    for e in out:
        body.append(f"## {e['field_id']} {e['name_zh'] if lang == 'zh' else e['name_en']}")
        if e.get("note"):
            body.append(f"- {e['note']}")
        for c in e["columns"]:
            body.append(f"- **{c['column_id']}** {c['name_zh'] if lang == 'zh' else c['name_en']} — {kind_name(c['kind'], lang)}, "
                        + L(lang, f"filled {c['filled']}/{c['of']}", f"有值 {c['filled']}/{c['of']}")
                        + (f"；该列在中文表里是英文原文（{c['text_language'].split('(')[1].split(' ')[0]}/{c['filled']} 个格子含中文）" if c.get("text_language") and lang == "zh" else ""))
            if c.get("values"):
                body.append(L(lang, "  - values: ", "  - 取值：") + ", ".join(f"{v['value']} ({v['count']})" for v in c["values"])
                            + (f" … {c['values_note']}" if c.get("values_note") else ""))
    if derived:
        body += ["", L(lang, "## Derived from label index (not columns of the source table)", "## 由标签索引派生（不是源表的列）")]
        for c in derived:
            body.append(f"- **{c['column_id']}** {c['name_zh'] if lang == 'zh' else c['name_en']} — {kind_name(c['kind'], lang)}, "
                        + L(lang, f"filled {c['filled']}/{c['of']}", f"有值 {c['filled']}/{c['of']}") + f", {dtag}")
            if c.get("values"):
                body.append(L(lang, "  - values: ", "  - 取值：") + ", ".join(f"{v['value']} ({v['count']})" for v in c["values"]))
    return emit(env, fmt, output, body, "fields")


# ---------------------------------------------------------------- search

def search(data: Data, query: Any = None, where: Any = None, fields_spec: Any = None, sort: str | None = None,
           offset: int = 0, limit: int = 20, match: str = "all", fmt: str | None = None, output: str | None = None) -> str:
    lang = data.lang
    limit, offset = int(limit), int(offset)
    if not 1 <= limit <= MAX_LIMIT:
        raise PtError(L(lang, f"--limit must be between 1 and {MAX_LIMIT}; page with --offset", f"--limit 必须在 1 到 {MAX_LIMIT} 之间；翻页请用 --offset"))
    if offset < 0:
        raise PtError(L(lang, "--offset must be 0 or more", "--offset 不能为负"))
    rows, conds, scores = filter_rows(data, where, query, match)
    tokens = [t.strip() for s in ([fields_spec] if isinstance(fields_spec, str) else list(fields_spec or [])) for t in str(s).split(",") if t.strip()]
    tokens = [t for t in tokens if t.lower() not in ("id", "name")]   # always returned anyway
    cols = [find_column(data, t) for t in tokens] if (tokens or fields_spec) else [data.column(t) for t in DEFAULT_COLUMNS]
    if sort:
        key, _, direction = sort.rpartition(":") if sort.rsplit(":", 1)[-1].lower() in ("asc", "desc") else (sort, "", "asc")
        scol = find_column(data, key)
        if scol.kind in ("text",):
            raise PtError(L(lang, f"cannot sort by {scol.en}: prose column", f"不能按 {scol.zh} 排序：它是长文本列"))
        if scol.kind == "categorical":
            keyf = lambda r: ((scol.value(r) or [""])[0]).casefold()
        else:
            keyf = lambda r: scol.value(r)
        have = [r for r in rows if scol.value(r) is not None]
        rest = [r for r in rows if scol.value(r) is None]
        have.sort(key=keyf, reverse=(direction.lower() == "desc"))
        rows = have + rest
    elif scores:
        rows = sorted(rows, key=lambda r: -scores[r["id"]])
    total = len(rows)
    page = rows[offset:offset + limit]
    items = [{"id": r["id"], "name": r["name"], **{c.name(lang): cell(c, r, lang) for c in cols}} for r in page]
    notes = zero_result_hint(data, conds, query, match) if total == 0 else []
    if lang == "zh":
        eo = english_only_columns(data)
        names = [c.name("zh") for c in cols if getattr(c, "id", None) in eo]
        if names and items:
            notes.append("列 " + "、".join(names) + " 在中文表里本身就是英文原文（源表没有中文），按原样给出，未翻译")
    env = {"data_version": data.version, "command": "table search", "lang": lang, "notes": notes,
           "total": total, "offset": offset, "limit": limit, "returned": len(items),
           "filters": [c.text(lang) for c in conds], "query": query or None, "sort": sort,
           "columns": [c.label(lang) for c in cols], "items": items}
    if total > offset + limit:
        env["next"] = f"--offset {offset + limit}"
    head = L(lang, f"{total} resources match" + (f" (showing {offset + 1}–{offset + len(items)})" if items else ""),
             f"{total} 个资源匹配" + (f"（显示第 {offset + 1}–{offset + len(items)} 个）" if items else ""))
    if conds:
        head += L(lang, "; filters: ", "；过滤条件：") + ", ".join(c.text(lang) for c in conds)
    if query:
        head += L(lang, "; query: ", "；查询词：") + " ".join(query)
    body = [head]
    if items:
        body += ["", *md_table(items, None, lang)]
    if env.get("next"):
        body.append(L(lang, f"\nmore: {env['next']}", f"\n下一页：{env['next']}"))
    return emit(env, fmt, output, body, "items")


# ---------------------------------------------------------------- stats

def stats(data: Data, group_by: Any = None, where: Any = None, query: Any = None, match: str = "all", top: int = 50,
          fmt: str | None = None, output: str | None = None) -> str:
    lang = data.lang
    rows, conds, _ = filter_rows(data, where, query, match)
    dims = [t.strip() for s in ([group_by] if isinstance(group_by, str) else list(group_by or [])) for t in str(s).split(",") if t.strip()]
    if len(dims) > 2:
        raise PtError(L(lang, "at most two --group-by fields", "--group-by 最多两个字段"))
    env: dict[str, Any] = {"data_version": data.version, "command": "table stats", "lang": lang, "notes": [],
                           "total_resources": len(rows), "filters": [c.text(lang) for c in conds], "query": query or None}
    selected = L(lang, f"{len(rows)} resources selected", f"选中 {len(rows)} 个资源") + (
        L(lang, " (filters: ", "（过滤条件：") + ", ".join(c.text(lang) for c in conds) + L(lang, ")", "）") if conds else "")
    if not dims:
        cols = all_columns(data)
        table, md_rows = [], []
        for c in cols:
            if isinstance(c, Column) and c.kind == "text":
                filled = sum(1 for r in rows if r["fields"].get(c.zh) not in (None, ""))
            else:
                filled = sum(1 for r in rows if c.value(r) is not None)
            table.append({"column_id": c.id, "name": c.name(lang), "kind": c.kind, "filled": filled,
                          "fill_rate": round(filled / len(rows), 3) if rows else None})
            md_rows.append({**table[-1], "kind": kind_name(c.kind, lang)})
        env["fill_rates"] = table
        env["notes"].append(L(lang, "overview: fill rate = resources with a value / resources selected; 'Not Specified' counts as a value",
                              "总览：填充率 = 有值的资源数 / 选中的资源数；“Not Specified”也算一个值"))
        if not rows:
            env["notes"] += zero_result_hint(data, conds, query, match)
        return emit(env, fmt, output, [selected, "", *md_table(md_rows, None, lang)], "fill_rates")
    cols = [find_column(data, d) for d in dims]
    for c in cols:
        if c.kind != "categorical":
            raise PtError(L(lang, f"cannot group by {c.en} ({c.kind}); group-by works on categorical fields. "
                                  "Use `table search --sort` for numbers, or a --where comparison to count.",
                            f"不能按 {c.zh}（{kind_name(c.kind, 'zh')}）分组；分组只适用于分类字段。"
                            "数值请用 `table search --sort`，或用 --where 比较来计数。"))
    missing = L(lang, "(missing)", "（缺失）")
    counter: Counter = Counter()
    for r in rows:
        vals = [c.value(r) or [missing] for c in cols]
        for combo in _product(vals):
            counter[combo] += 1
    ordered = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
    keys = [c.name(lang) for c in cols]
    table = [{**dict(zip(keys, combo)), "count": n} for combo, n in ordered[:int(top)]]
    env["group_by"] = keys
    env["groups"] = table
    env["n_groups"] = len(ordered)
    env["notes"].append(L(lang, "a resource with several values counts once in each of them, so group counts can add up to more than the "
                                f"number of resources; '{missing}' = the field has no value",
                          f"一个资源有多个取值时在每个取值里各计一次，所以各组之和可能大于资源数；“{missing}”= 该字段没有取值"))
    if len(ordered) > int(top):
        env["notes"].append(L(lang, f"{len(ordered) - int(top)} more groups not shown; raise --top", f"还有 {len(ordered) - int(top)} 组未显示；请加大 --top"))
    if not rows:
        env["notes"] += zero_result_hint(data, conds, query, match)
    body = [selected + L(lang, f"; grouped by {', '.join(keys)}", f"；按 {'、'.join(keys)} 分组"), "", *md_table(table, None, lang)]
    return emit(env, fmt, output, body, "groups")


def _product(lists: list[list[str]]):
    combos = [()]
    for lst in lists:
        combos = [c + (v,) for c in combos for v in lst]
    return combos
