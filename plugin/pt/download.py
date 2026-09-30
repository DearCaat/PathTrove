"""download domain: how a resource can be obtained. It gives the plan and the facts; it never downloads a dataset."""
from __future__ import annotations

from typing import Any

from .data import Data
from .errors import PtError
from .i18n import L
from .parse import SECTION_HELP, SECTION_ORDER, parse_guide
from .render import emit, md_lines, parse_layers
from .report import load

TEST_LABEL = {
    "en": (
        "Each item is the record of one download test, tested from PathTrove's test environment on the date shown (tested_at); the network "
        "conditions are those recorded in the item's note, shown as recorded where the record has one (nothing is inferred about where the test ran; 'direct failed' "
        "can mean 'blocked from there'). It is NOT the size of the dataset and NOT a property of the resource: `bytes_received` is what "
        "the test downloaded (often a 1 MiB sample) and `content_length_bytes` is the size of the file(s) the test named, which may be "
        "one archive."),
    "zh": (
        "每一项是一次下载测试的记录，由 PathTrove 的测试环境在所示日期（tested_at）完成；网络条件以该项备注所记为准，原样给出"
        "（不推断测试是在哪里做的；“直连失败”可能只是“从那里被拦截”）。它不是数据集的大小，也不是该资源的属性："
        "`bytes_received` 是测试实际下载的字节数（常常只是 1 MiB 样本），`content_length_bytes` 是测试所指定文件的大小，可能只是一个压缩包。"),
}


def guide_of(data: Data, row: dict[str, Any]) -> tuple[dict[str, Any] | None, str, str | None, Any]:
    """(parsed guide, language used, note, path)."""
    if data.lang == "en":
        p = data.guide_path(row, "en")
        if p:
            return parse_guide(str(p)), "en", None, p
        zh = data.guide_path(row, "zh")
        note = ("no English translation of this guide in the bundle (missing or it did not pass the translation check); "
                "the original Chinese text is shown and is labelled lang=zh")
        return (parse_guide(str(zh)) if zh else None), "zh", note, zh
    p = data.guide_path(row, "zh")
    return (parse_guide(str(p)) if p else None), "zh", None if p else "数据包里没有这份下载指南", p


def section(g: dict[str, Any] | None, name: str) -> dict[str, Any] | None:
    return next((s for s in (g or {}).get("sections", []) if s["name"] == name), None)


def col_value(data: Data, row: dict[str, Any], col_id: str) -> Any:
    return data.column(col_id).value(row)


def sources(parsed: dict[int, dict[str, Any]], fids: list[int], lang: str) -> dict[str, Any]:
    return {L(lang, f"report field {f}", f"报告字段 {f}"): (parsed.get(f) or {}).get("source") or None for f in fids}


def test_record(g: dict[str, Any] | None) -> dict[str, Any] | None:
    """The download test as {value, text, tested_at, schema}, from either JSON block schema."""
    if not g:
        return None
    dv, blk = g["dv"], g["block"]
    if dv:
        ts, direct, proxy = dv.get("total_size") or {}, dv.get("direct") or {}, dv.get("proxy") or {}
        return {
            "schema": "download_verification", "tested_at": dv.get("tested_at"),
            "value": {"method_status": dv.get("download_method_status"),
                      "direct": {"status": direct.get("status"), "http_status": direct.get("http_status"),
                                 "bytes_received": direct.get("bytes_received")},
                      "proxy": {"status": proxy.get("status"), "used": proxy.get("used")},
                      "content_length_bytes": ts.get("content_length_bytes"),
                      "downloaded_bytes": ts.get("downloaded_bytes"),
                      "files": [{"url": x.get("url"), "bytes_received": x.get("bytes"), "disposition": x.get("disposition")}
                                for x in dv.get("files") or []],
                      "cleanup": dv.get("cleanup")},
            "text": {"download_method": dv.get("download_method"), "direct": direct.get("note"), "proxy": proxy.get("note"),
                     "total_size": ts.get("note"), "test_note": dv.get("note") or (blk or {}).get("note")},
        }
    if g["schema"] == "3.0":
        net, ds = blk.get("network") or {}, blk.get("download_size") or {}
        return {
            "schema": "3.0", "tested_at": blk.get("download_time"),
            "value": {"method_status": None,
                      "network": {"environment": net.get("environment"), "proxy_status": net.get("proxy_status"),
                                  "proxy_region": net.get("proxy_region"),
                                  "mainland_network_download": net.get("mainland_network_download")},
                      "declared_download_size": {"value": ds.get("value"), "unit": ds.get("unit"), "verified": ds.get("verified"),
                                                "source": ds.get("source")},
                      "files": []},
            "text": {"network": net.get("notes")},
        }
    return None


def item_lang(lang: str, used: set[str]) -> str:
    """The language of the text in an item: the call's language, or zh when an English call had to fall back to the Chinese original."""
    return lang if used <= {lang} else "zh"


def lang_of(lang: str, used: set[str]) -> str:
    return lang if used <= {lang} else f"{lang} (fallback: {','.join(sorted(used))})"


def plan(data: Data, resource: Any, layer: Any = None, fmt: str | None = None, output: str | None = None) -> str:
    lang = data.lang
    rows = data.resources(resource)
    layers = parse_layers(layer, ("value",), lang)
    items, notes, used = [], [], set()
    for r in rows:
        parsed, ulang, note = load(data, r)
        g, glang, gnote, gpath = guide_of(data, r)
        used |= {ulang, glang}
        notes += [f"{r['name']}: {n}" for n in (note, gnote) if n]
        rec = test_record(g)
        it: dict[str, Any] = {"id": r["id"], "name": r["name"], "lang": item_lang(lang, {ulang, glang})}
        if "value" in layers:
            it["value"] = {"open_status": col_value(data, r, "3-1"), "license": col_value(data, r, "32-1"),
                           "download_url": col_value(data, r, "30-1")}
        # No structured value exists for the access gate and for the method: show the text, labelled (option A).
        it["access_gate"] = {"value": None,
                             "note": L(lang, "no structured value in this release: whether an application or login is needed is only written in prose",
                                       "本版数据没有结构化取值：是否需要申请或登录只写在文字里"),
                             "text": (parsed.get(4) or {}).get("text"),
                             "text_from": L(lang, f"report field 4 (open-access notes), {ulang}", f"报告字段 4（开源说明），{ulang}")}
        it["download_method"] = {"value": None,
                                 "note": L(lang, "no structured value in this release: the method is a sentence in the download test record",
                                           "本版数据没有结构化取值：下载方式是下载测试记录里的一句话"),
                                 "text": ((rec or {}).get("text") or {}).get("download_method"),
                                 "text_from": L(lang, f"guide JSON block (download test of {(rec or {}).get('tested_at')})",
                                                f"下载指南 JSON 块（{(rec or {}).get('tested_at')} 的下载测试）") if rec else None}
        if rec:
            it["last_test"] = {"tested_at": rec["tested_at"], "method_status": rec["value"].get("method_status"),
                               "note": L(lang, "a test record, not a property of the resource; `download test` explains it",
                                         "是一次测试记录，不是资源的属性；说明见 `download test`")}
        if "text" in layers:
            it["text"] = {"openness_reasoning (field 3)": (parsed.get(3) or {}).get("text"),
                          "license_reasoning (field 32)": (parsed.get(32) or {}).get("text")}
        if "source" in layers:
            it["source"] = {**sources(parsed, [3, 4, 30, 32], lang), "guide": data.rel(gpath) if gpath else None}
        items.append(it)
    env = {"data_version": data.version, "command": "download plan", "lang": lang_of(lang, used),
           "layers": list(layers), "notes": notes, "items": items}
    body = []
    for it in items:
        body += [f"## {it['name']} ({it['id']})", *md_lines({k: v for k, v in it.items() if k not in ("id", "name")}, 0, lang), ""]
    return emit(env, fmt, output, body, "items")


def objects(data: Data, resource: Any, layer: Any = None, fmt: str | None = None, output: str | None = None) -> str:
    lang = data.lang
    rows = data.resources(resource)
    layers = parse_layers(layer, ("value",), lang)
    items, notes, used = [], [], set()
    for r in rows:
        parsed, ulang, note = load(data, r)
        g, glang, gnote, gpath = guide_of(data, r)
        used |= {ulang, glang}
        notes += [f"{r['name']}: {n}" for n in (note, gnote) if n]
        sec = section(g, "objects")
        it = {"id": r["id"], "name": r["name"], "lang": item_lang(lang, {ulang, glang}),
              "objects": {"value": None,
                          "note": L(lang, "no structured list of downloadable objects in this release; the text is the guide's download-objects section",
                                    "本版数据没有结构化的可下载对象清单；下面的文字是指南的“下载对象”一节"),
                          "text": sec["text"] if sec else None,
                          "text_from": (L(lang, f"guide section “{sec['heading']}” ({glang}), {data.rel(gpath)}",
                                          f"指南章节“{sec['heading']}”（{glang}），{data.rel(gpath)}") if sec
                                        else L(lang, "no such section in this guide", "这份指南没有这一节"))},
              "size": {"value": None,
                       "note": L(lang, "no structured dataset size in this release; the text is the report's storage-size field. "
                                       "Sizes inside the tables above are prose too. Sizes in `download test` are test bytes, not dataset size",
                                 "本版数据没有结构化的数据集大小；下面的文字是报告的存储量字段。上面表格里的大小也只是文字。"
                                 "`download test` 里的大小是测试字节数，不是数据集大小"),
                       "text": (parsed.get(15) or {}).get("text"),
                       "text_from": L(lang, f"report field 15 (storage size), {ulang}: text, not a structured value",
                                      f"报告字段 15（存储量），{ulang}：文字，不是结构化取值")}}
        if "source" in layers:
            it["size"]["source"] = (parsed.get(15) or {}).get("source") or None
        items.append(it)
    env = {"data_version": data.version, "command": "download objects", "lang": lang_of(lang, used),
           "layers": ["text", *[l for l in layers if l == "source"]], "notes": notes, "items": items}
    body = []
    frm, src = L(lang, "from: ", "出处："), L(lang, "source:", "来源：")
    for it in items:
        body += [f"## {it['name']} ({it['id']})", L(lang, "### objects", "### 下载对象"), f"- {it['objects']['note']}", f"- {frm}{it['objects']['text_from']}", ""]
        body += ([ln for ln in (it["objects"]["text"] or "—").splitlines()] + [""])
        body += [L(lang, "### size", "### 大小"), f"- {it['size']['note']}", f"- {frm}{it['size']['text_from']}", ""]
        body += ([ln for ln in (it["size"]["text"] or "—").splitlines()] + [""])
        if it["size"].get("source"):
            body += [src] + [f"- {s}" for s in it["size"]["source"]] + [""]
    return emit(env, fmt, output, body, "items")


def test(data: Data, resource: Any, layer: Any = None, fmt: str | None = None, output: str | None = None) -> str:
    lang = data.lang
    rows = data.resources(resource)
    layers = parse_layers(layer, ("value",), lang)
    items, notes, used = [], [], set()
    for r in rows:
        g, glang, gnote, gpath = guide_of(data, r)
        used.add(glang)
        if gnote:
            notes.append(f"{r['name']}: {gnote}")
        rec = test_record(g)
        it: dict[str, Any] = {"id": r["id"], "name": r["name"], "lang": glang}
        if rec is None:
            it["record"] = None
            it["note"] = L(lang, "this guide has no download test record", "这份指南没有下载测试记录")
        else:
            it["tested_at"] = rec["tested_at"]
            it["schema"] = rec["schema"] + ("" if rec["schema"] == "download_verification" else L(
                lang, " (different JSON block: no status/direct/proxy/files; see value)", "（另一种 JSON 块：没有 status/direct/proxy/files；见 value）"))
            if "value" in layers:
                it["value"] = rec["value"]
            if "text" in layers:
                it["text"] = rec["text"]
            if "source" in layers:
                it["source"] = {"guide": data.rel(gpath), "json_block": L(lang, "first block of the guide", "指南的第一个代码块"),
                                "tested_at": rec["tested_at"]}
        items.append(it)
    env = {"data_version": data.version, "command": "download test", "lang": lang_of(lang, used), "layers": list(layers),
           "read_this_as": TEST_LABEL[lang], "notes": notes, "items": items}
    body = [L(lang, "**Read this as**: ", "**请这样理解**：") + TEST_LABEL[lang], ""]
    for it in items:
        body += [f"## {it['name']} ({it['id']})", *md_lines({k: v for k, v in it.items() if k not in ("id", "name")}, 0, lang), ""]
    return emit(env, fmt, output, body, "items")


def guide(data: Data, resource: Any, section_spec: Any = None, fmt: str | None = None, output: str | None = None) -> str:
    lang = data.lang
    rows = data.resources(resource)
    tokens = [t.strip().lower() for s in ([section_spec] if isinstance(section_spec, str) else list(section_spec or []))
              for t in str(s).split(",") if t.strip()]
    bad = [t for t in tokens if t != "all" and t not in SECTION_ORDER]
    if bad:
        raise PtError(L(lang, f"unknown section {bad}; sections: {', '.join(SECTION_ORDER)} or 'all'. "
                              "Both guide templates are mapped onto these names; omit --section for the outline.",
                        f"未知的章节 {bad}；可用章节：{', '.join(SECTION_ORDER)}，或 all。两种指南模板都映射到这些名称；不加 --section 可看目录。"))
    items, notes, used = [], [], set()
    for r in rows:
        g, glang, gnote, gpath = guide_of(data, r)
        used.add(glang)
        if gnote:
            notes.append(f"{r['name']}: {gnote}")
        if g is None:
            items.append({"id": r["id"], "name": r["name"], "guide": None})
            continue
        secs = g["sections"]
        chosen = secs if "all" in tokens else [s for s in secs if s["name"] in tokens]
        it: dict[str, Any] = {"id": r["id"], "name": r["name"], "lang": glang, "template": g["template"],
                              "outline": [{"section": s["name"], "heading": s["heading"], "chars": len(s["text"])} for s in secs]}
        missing = [t for t in tokens if t != "all" and not any(s["name"] == t for s in secs)]
        if missing:
            it["not_in_this_guide"] = L(lang, f"{', '.join(missing)} (this is a {g['template']}-template guide)",
                                        f"{', '.join(missing)}（这是 {g['template']} 模板的指南）")
        if chosen:
            it["sections"] = [{"section": s["name"], "heading": s["heading"], "text": s["text"]} for s in chosen]
        it["source"] = data.rel(gpath)
        items.append(it)
    env = {"data_version": data.version, "command": "download guide", "lang": lang_of(lang, used), "notes": notes, "items": items}
    body = []
    for it in items:
        body.append(f"## {it['name']} ({it['id']})")
        if it.get("guide", 1) is None:
            body += [L(lang, "no guide in the bundle", "数据包里没有指南"), ""]
            continue
        body.append(L(lang, f"template: {it['template']}; lang: {it['lang']}; file: {it['source']}",
                      f"模板：{it['template']}；语言：{it['lang']}；文件：{it['source']}"))
        body.append(L(lang, "outline: ", "目录：") + "; ".join(f"`{o['section']}` “{o['heading']}” ({o['chars']} " + L(lang, "chars", "字符") + ")"
                                                                 for o in it["outline"]))
        if it.get("not_in_this_guide"):
            body.append(L(lang, "not in this guide: ", "本指南没有：") + it["not_in_this_guide"])
        if not it.get("sections"):
            body.append(L(lang, "(no section selected: add --section NAME[,NAME] or --section all; this guide has: ",
                          "（未选章节：请加 --section 名称[,名称] 或 --section all；这份指南有：")
                        + ", ".join(o["section"] for o in it["outline"]) + L(lang, ")", "）"))
        for s in it.get("sections", []):
            body += ["", f"### {s['section']} — “{s['heading']}”", s["text"]]
        body.append("")
    return emit(env, fmt, output, body, "items")
