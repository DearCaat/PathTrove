"""report domain: the three layers (value / text / source) of the report fields, and term search in them."""
from __future__ import annotations

import json
from typing import Any

from .data import Data
from .errors import PtError
from .i18n import L
from .parse import parse_report
from .render import emit, md_table, parse_layers

ALWAYS_RETURNED = ("id", "name")


def load(data: Data, row: dict[str, Any], lang: str | None = None) -> tuple[dict[int, dict[str, Any]], str, str | None]:
    """(parsed fields, language actually used, note)."""
    lang = lang or data.lang
    if lang == "en":
        path = data.report_path(row, "en")
        if path:
            return parse_report(str(path)), "en", None
        note = ("no English translation of this report in the bundle (missing or it did not pass the translation check); "
                "the original Chinese text is shown and is labelled lang=zh")
        path = data.report_path(row, "zh")
        return (parse_report(str(path)) if path else {}), "zh", note
    path = data.report_path(row, "zh")
    note = None if path else L(data.lang, "report file not found in the bundle", "数据包里没有这份报告文件")
    return (parse_report(str(path)) if path else {}), "zh", note


def field_entry(parsed: dict[str, Any] | None, layers: tuple[str, ...], lang: str) -> dict[str, Any]:
    if parsed is None:
        return {"missing": L(lang, "this report has no such field", "这份报告没有该字段")}
    e: dict[str, Any] = {}
    if "value" in layers:
        e["value"] = parsed["value"]
        if parsed.get("value_note"):
            e["value_note"] = parsed["value_note"]
        if parsed.get("value_raw"):
            e["value_raw"] = parsed["value_raw"]
        if not parsed["has_value_block"]:
            e["value"] = None
            e["value_note"] = L(lang, "no structured value for this field: the report gives text only", "该字段没有结构化取值：报告只给了文字")
    if "text" in layers:
        e["text"] = parsed["text"]
    if "source" in layers:
        e["source"] = parsed["source"]
    absent = [l for l in ("value", "text", "source") if l not in layers]
    if absent:
        avail = []
        if "value" in absent and parsed["has_value_block"]:
            avail.append("value")
        if "text" in absent and parsed["text"]:
            avail.append(f"text ({len(parsed['text'])} " + L(lang, "chars", "字符") + ")")
        if "source" in absent and parsed["source"]:
            avail.append(f"source ({len(parsed['source'])})")
        if avail:
            e["more_layers"] = ", ".join(avail) + L(lang, " — add --layer", " —— 加 --layer 查看")
    return e


def split_fields(spec: Any) -> tuple[list[str], bool]:
    """Field tokens without `id` / `name` (always returned), and whether any were given."""
    tokens = [t.strip() for s in ([spec] if isinstance(spec, str) else list(spec or [])) for t in str(s).split(",") if t.strip()]
    keep = [t for t in tokens if t.lower() not in ALWAYS_RETURNED]
    return keep, bool(tokens)


def get(data: Data, resource: Any, fields_spec: Any, layer: Any = None, fmt: str | None = None, output: str | None = None) -> str:
    lang = data.lang
    rows = data.resources(resource)
    tokens, given = split_fields(fields_spec)
    if not given:
        raise PtError(L(lang, "give --fields: ids, Chinese or English names, comma-separated, or 'all' (see `table fields`)",
                        "请给出 --fields：字段编号、中文名或英文名（逗号分隔），或 all（见 `table fields`）"))
    fids = data.field_ids_from(tokens)
    layers = parse_layers(layer, ("value",), lang)
    items, notes, used = [], [], set()
    for r in rows:
        parsed, used_lang, note = load(data, r)
        used.add(used_lang)
        if note:
            notes.append(f"{r['name']}: {note}")
        items.append({"id": r["id"], "name": r["name"], "lang": used_lang,
                      "fields": [{"field_id": f, "name": data.field_name(f), **field_entry(parsed.get(f), layers, lang)} for f in fids]})
    env = {"data_version": data.version, "command": "report get", "lang": lang if used <= {lang} else f"{lang} (fallback: {','.join(sorted(used))})",
           "layers": list(layers), "notes": notes, "items": items}
    body: list[str] = []
    for it in items:
        body.append(f"## {it['name']} ({it['id']})")
        for f in it["fields"]:
            body.append(f"### {f['field_id']}. {f['name']}")
            for k, v in f.items():
                if k in ("field_id", "name"):
                    continue
                kk = L(lang, k, {"value": "值", "text": "文本", "source": "来源", "value_note": "值说明", "value_raw": "原始值",
                                 "more_layers": "还有其他层", "missing": "缺失"}.get(k, k))
                if k in ("value", "value_raw") and not isinstance(v, str):
                    body.append(f"- **{kk}**: " + (json.dumps(v, ensure_ascii=False) if v is not None else "—"))
                elif k == "source":
                    body.append(f"- **{kk}**:" + ("" if v else " —"))
                    body += [f"  - {s}" for s in v]
                elif isinstance(v, str) and (len(v) > 200 or "\n" in v):
                    body.append(f"- **{kk}**:")
                    body += [f"  > {ln}" for ln in v.splitlines()]
                else:
                    body.append(f"- **{kk}**: {v if v not in (None, '') else '—'}")
        body.append("")
    return emit(env, fmt, output, body, "items")


def snippet(text: str, needle: str, width: int = 90) -> str:
    text = " ".join(text.split())
    i = text.casefold().find(needle.casefold())
    a, b = max(0, i - width), min(len(text), i + len(needle) + width)
    return ("…" if a else "") + text[a:b] + ("…" if b < len(text) else "")


def find(data: Data, text: Any, fields_spec: Any = None, resource: Any = None, layer: Any = None,
         limit: int = 30, fmt: str | None = None, output: str | None = None) -> str:
    lang = data.lang
    terms = [t.strip() for s in ([text] if isinstance(text, str) else list(text or [])) for t in str(s).split("|") if t.strip()]
    if not terms:
        raise PtError(L(lang, "give --text TERM (several terms: TERM|TERM, matched literally, case-insensitive)",
                        "请给出 --text 词（多个词：词|词，按字面匹配，不分大小写）"))
    fids = data.field_ids_from(fields_spec) if fields_spec else list(data.field_ids)
    layers = parse_layers(layer, ("value", "text"), lang)
    rows = data.resources(resource) if resource else data.rows
    limit = int(limit)
    hits, fallback = [], 0
    matched_resources = set()
    total = 0
    for r in rows:
        path = data.report_path(r) or data.report_path(r, "zh")
        if path is None or not any(t.casefold() in path.read_text(encoding="utf-8").casefold() for t in terms):
            fallback += lang == "en" and data.report_path(r, "en") is None
            continue                                    # cheap pre-check: parse only reports that contain a term somewhere
        parsed, used_lang, _ = load(data, r)
        fallback += used_lang != lang
        for f in fids:
            p = parsed.get(f)
            if not p:
                continue
            for lay in layers:
                chunks = {"value": [json.dumps(p["value"], ensure_ascii=False)] if p["value"] is not None else
                          ([p["value_raw"]] if p.get("value_raw") else []),
                          "text": [p["text"]] if p["text"] else [], "source": p["source"]}[lay]
                for ch in chunks:
                    term = next((t for t in terms if t.casefold() in ch.casefold()), None)
                    if term:
                        total += 1
                        matched_resources.add(r["id"])
                        if len(hits) < limit:
                            hits.append({"id": r["id"], "name": r["name"], "field_id": f, "field": data.field_name(f),
                                         "layer": lay, "lang": used_lang, "term": term, "snippet": snippet(ch, term)})
                        break
    notes = []
    if lang == "en" and fallback:
        notes.append(f"{fallback} of {len(rows)} resources have no English report in the bundle; their Chinese text was searched (rows marked lang=zh), "
                     "so an English term may miss them")
    if total == 0:
        notes.append(L(lang, "0 matches. Terms are matched literally: try a synonym, an abbreviation, or the Chinese/English form; "
                             "widen --layer (value,text,source) or --fields.",
                       "0 处匹配。词按字面匹配：请换同义词、缩写，或中/英文写法；也可放宽 --layer（value,text,source）或 --fields。"))
    if total > len(hits):
        notes.append(L(lang, f"{total - len(hits)} more matches not shown; raise --limit or narrow --fields / --resource",
                       f"还有 {total - len(hits)} 处匹配未显示；请加大 --limit，或缩小 --fields / --resource"))
    env = {"data_version": data.version, "command": "report find", "lang": lang, "notes": notes, "terms": terms,
           "layers": list(layers), "resources_searched": len(rows), "matches": total, "resources_matched": len(matched_resources),
           "items": hits}
    fsel = L(lang, "all", "全部") if len(fids) == len(data.field_ids) else ",".join(map(str, fids))
    body = [L(lang, f"{total} matches in {len(matched_resources)} of {len(rows)} resources (layers: {','.join(layers)}; fields: {fsel})",
              f"{len(rows)} 个资源中 {len(matched_resources)} 个共 {total} 处匹配（层：{','.join(layers)}；字段：{fsel}）"), ""]
    if hits:
        body += md_table(hits, ["name", "id", "field_id", "layer", "lang", "snippet"], lang)
    return emit(env, fmt, output, body, "items")
