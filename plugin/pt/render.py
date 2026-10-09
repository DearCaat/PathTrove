"""Output: markdown / json / ndjson, --layer selection, --output to a file. Markdown labels follow the call's language;
JSON keys are identifiers and stay English."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import PtError
from .i18n import L

LAYERS = ("value", "text", "source")
FORMATS = ("md", "json", "ndjson")
MAX_CHARS = 60_000          # stdout cap; larger results must go to --output or be narrowed

# Markdown labels (the keys of the result records) in Chinese. Keys not listed are shown as they are.
KEYS_ZH = {
    "value": "值", "text": "文本", "source": "来源", "value_note": "值说明", "value_raw": "原始值", "more_layers": "还有其他层",
    "id": "id", "name": "名称", "field": "字段", "field_id": "字段编号", "layer": "层", "term": "词", "snippet": "片段",
    "kind": "类型", "filled": "有值", "of": "共", "fill_rate": "填充率", "count": "数量", "column_id": "列", "n_values": "取值数",
    "values": "取值", "note": "说明", "tested_at": "测试日期", "schema": "记录格式", "record": "记录", "open_status": "开放程度",
    "license": "许可证", "download_url": "下载链接", "access_gate": "访问门槛", "download_method": "下载方式", "last_test": "最近测试",
    "method_status": "方式状态", "direct": "直连", "proxy": "代理", "status": "状态", "http_status": "HTTP 状态码",
    "bytes_received": "已收字节", "used": "是否使用", "content_length_bytes": "所测文件大小（字节）", "downloaded_bytes": "测试下载字节",
    "files": "文件", "url": "链接", "disposition": "结果", "cleanup": "清理", "network": "网络", "environment": "环境",
    "proxy_status": "代理状态", "proxy_region": "代理地区", "mainland_network_download": "大陆网络下载",
    "declared_download_size": "声明的下载大小", "unit": "单位", "verified": "已核实", "objects": "下载对象", "size": "大小",
    "text_from": "文本出处", "template": "模板", "outline": "目录", "section": "章节", "heading": "标题", "chars": "字符数",
    "sections": "章节", "guide": "指南", "not_in_this_guide": "本指南没有", "lang": "语言", "file": "文件", "task_name": "任务名",
    "task_type": "任务类型", "level": "层级", "samples": "样本数", "size_bytes": "大小（字节）", "label_files": "标签文件数",
    "matching": "匹配数", "labels": "标签", "samples_observed": "统计到的样本数", "samples_declared_by_source": "来源声明的样本数",
    "n_classes": "类别数", "class_distribution": "类别分布", "class_names": "类别名", "split_distribution": "划分分布",
    "raw_file": "原始文件", "sha256": "sha256", "fetch": "下载命令", "class_distribution_note": "类别分布说明",
    "task_schema": "任务结构", "limitations": "局限", "class_distribution_basis": "类别分布依据", "provenance": "出处",
    "levels": "层级", "split": "划分", "split_parts": "划分部分", "files_with_split": "有官方划分的文件数", "has_official_split": "有官方划分", "split_counts": "划分数量", "samples_without_split": "无划分样本数", "split_notes": "划分相关文字", "file_list": "文件列表", "task_types": "任务类型", "files_count": "文件数", "openness_reasoning (field 3)": "开放程度依据（字段 3）",
    "license_reasoning (field 32)": "许可证依据（字段 32）", "json_block": "JSON 块", "tested_from": "测试环境",
    "record_id": "record id", "data_version": "数据版本", "installed": "已安装", "location": "位置", "cache_root": "缓存目录",
    "archive": "数据包", "hf_endpoint": "HF 地址", "bundle_override": "PATHTROVE_BUNDLE 覆盖", "path": "路径", "bytes": "字节",
    "records": "记录数", "written_to": "已写入", "format": "格式", "message": "信息", "direct_note": "直连说明", "proxy_note": "代理说明",
    "total_size": "总大小说明", "test_note": "测试备注", "download_method_text": "下载方式原文", "network_note": "网络说明",
    "unpacked_bytes": "解压后字节", "sources": "来源", "value_distribution": "值分布", "lang_note": "语言说明",
}
KEYS_EN = {"record_id": "record id"}


def key(k: str, lang: str) -> str:
    return KEYS_ZH.get(k, k) if lang == "zh" else k


def parse_layers(spec: Any, default: tuple[str, ...] = ("value",), lang: str = "en") -> tuple[str, ...]:
    if spec in (None, "", []):
        return default
    tokens = [t.strip().lower() for s in ([spec] if isinstance(spec, str) else spec) for t in str(s).split(",") if t.strip()]
    if "all" in tokens:
        return LAYERS
    bad = [t for t in tokens if t not in LAYERS]
    if bad:
        raise PtError(L(lang, f"unknown layer {bad}; use value, text, source (comma-separated) or all",
                        f"未知的层 {bad}；可用 value、text、source（逗号分隔）或 all"))
    return tuple(t for t in LAYERS if t in tokens)


def check_format(fmt: str | None, lang: str = "en") -> str:
    fmt = (fmt or "md").lower()
    if fmt not in FORMATS:
        raise PtError(L(lang, f"unknown format {fmt!r}; use md, json or ndjson", f"未知的格式 {fmt!r}；可用 md、json 或 ndjson"))
    return fmt


# ---------------------------------------------------------------- markdown

def scalar(v: Any, lang: str = "en") -> str:
    if v is None or v == [] or v == "":
        return "—"
    if isinstance(v, bool):
        return L(lang, "yes", "是") if v else L(lang, "no", "否")
    if isinstance(v, list):
        return "; ".join(scalar(x, lang) for x in v)
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False)
    return str(v).replace("\n", " ").replace("|", "\\|")


def is_flat(v: Any) -> bool:
    return isinstance(v, (str, int, float, bool)) or v is None or (isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v))


def md_table(rows: list[dict[str, Any]], columns: list[str] | None = None, lang: str = "en") -> list[str]:
    columns = columns or list(dict.fromkeys(k for r in rows for k in r))
    lines = ["| " + " | ".join(key(c, lang) for c in columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(scalar(r.get(c), lang) for c in columns) + " |")
    return lines


def md_lines(v: Any, depth: int = 0, lang: str = "en") -> list[str]:
    pad = "  " * depth
    if isinstance(v, dict):
        lines: list[str] = []
        for k, x in v.items():
            kk = key(k, lang)
            if is_flat(x) and not (isinstance(x, str) and ("\n" in x or len(x) > 240)):
                lines.append(f"{pad}- **{kk}**: {scalar(x, lang)}")
            elif isinstance(x, str):
                lines.append(f"{pad}- **{kk}**:")
                lines += [f"{pad}  > {ln}" if ln.strip() else f"{pad}  >" for ln in x.splitlines()]
            elif isinstance(x, list) and x and all(isinstance(i, dict) and all(is_flat(j) for j in i.values()) for i in x):
                lines.append(f"{pad}- **{kk}**:")
                lines += [f"{pad}  {ln}" for ln in md_table(x, None, lang)]
            elif isinstance(x, list):
                lines.append(f"{pad}- **{kk}**:")
                for i in x:
                    lines += md_lines(i, depth + 1, lang) if isinstance(i, dict) else [f"{pad}  - {scalar(i, lang)}"]
            elif x in ({}, None):
                lines.append(f"{pad}- **{kk}**: —")
            else:
                lines.append(f"{pad}- **{kk}**:")
                lines += md_lines(x, depth + 1, lang)
        return lines
    if isinstance(v, list):
        return [f"{pad}- {scalar(x, lang)}" if is_flat(x) else f"{pad}-" for x in v] if all(is_flat(x) for x in v) else \
            [ln for x in v for ln in ([f"{pad}-"] + md_lines(x, depth + 1, lang))]
    return [f"{pad}{scalar(v, lang)}"]


def header(envelope: dict[str, Any]) -> str:
    lang = envelope.get("lang") or "en"
    parts = [L(lang[:2], "PathTrove data ", "PathTrove 数据 ") + envelope["data_version"], envelope["command"]]
    parts.append(f"lang={lang}")
    return "[" + " · ".join(parts) + "]"


def to_markdown(envelope: dict[str, Any], body: list[str] | None = None) -> str:
    lang = (envelope.get("lang") or "en")[:2]
    lines = [header(envelope)]
    for n in envelope.get("notes") or []:
        lines.append(L(lang, "note: ", "说明：") + str(n))
    lines.append("")
    if body is None:
        rest = {k: v for k, v in envelope.items() if k not in ("data_version", "command", "lang", "notes")}
        body = md_lines(rest, 0, lang)
    return "\n".join(lines + body).rstrip() + "\n"


# ---------------------------------------------------------------- final output

def emit(envelope: dict[str, Any], fmt: str | None, output: str | None, md_body: list[str] | None = None,
         items_key: str | None = None) -> str:
    """Render an envelope. With --output the full result goes to the file and a short summary is returned."""
    lang = (envelope.get("lang") or "en")[:2]
    fmt = check_format(fmt, lang)
    if fmt == "json":
        text = json.dumps(envelope, ensure_ascii=False, indent=1) + "\n"
    elif fmt == "ndjson":
        items = envelope.get(items_key) if items_key else None
        if items is None:
            raise PtError(L(lang, "--format ndjson is only available for commands that return a list of records "
                                  "(table search, table fields, report get, report find, label list, label get)",
                            "--format ndjson 只适用于返回记录列表的命令（table search、table fields、report get、report find、label list、label get）"))
        meta = {k: v for k, v in envelope.items() if k != items_key}
        meta[items_key] = f"{len(items)} records follow, one JSON object per line"
        text = json.dumps({"_meta": meta}, ensure_ascii=False) + "\n" + "".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items)
    else:
        text = to_markdown(envelope, md_body)
    if output:
        path = Path(output).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        n_items = len(envelope[items_key]) if items_key and isinstance(envelope.get(items_key), list) else None
        summary = {"data_version": envelope["data_version"], "command": envelope["command"], "written_to": str(path.resolve()),
                   "format": fmt, "bytes": len(text.encode("utf-8")), "records": n_items}
        if fmt == "json":
            return json.dumps(summary, ensure_ascii=False, indent=1) + "\n"
        return (f"{header(envelope)}\n" + L(lang, f"result written to {summary['written_to']} ({summary['format']}, {summary['bytes']} bytes"
                                              + (f", {n_items} records" if n_items is not None else "") + "). Read the file for the content.\n",
                                              f"结果已写入 {summary['written_to']}（{summary['format']}，{summary['bytes']} 字节"
                                              + (f"，{n_items} 条记录" if n_items is not None else "") + "）。内容请读该文件。\n"))
    if len(text) > MAX_CHARS and fmt != "md":
        raise PtError(L(lang, f"the {fmt} result is {len(text)} characters, more than the {MAX_CHARS} allowed on stdout "
                              "(cutting it would break the format); add --output FILE or narrow the request",
                        f"{fmt} 结果有 {len(text)} 个字符，超过标准输出允许的 {MAX_CHARS}（截断会破坏格式）；请加 --output FILE 或缩小请求"))
    if len(text) > MAX_CHARS:
        cut = text[:MAX_CHARS].rsplit("\n", 1)[0]
        return cut + L(lang, f"\n[output cut at {MAX_CHARS} characters of {len(text)}; narrow the request "
                             "(fewer resources or fields, smaller --limit) or add --output FILE to write it all to a file]\n",
                       f"\n[输出在 {len(text)} 个字符中的第 {MAX_CHARS} 处截断；请缩小请求（更少的资源或字段、更小的 --limit），"
                       "或加 --output FILE 把全部内容写入文件]\n")
    return text
