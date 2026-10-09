"""label domain: which label files a resource has, what they contain (from the bundled index), and fetching the raw file."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from . import net, table
from .data import Data
from .errors import PtError
from .i18n import L
from .render import emit, md_lines, md_table, parse_layers


PARTS = ("train", "val", "test")
PART_ALIASES = {"train": "train", "training": "train", "训练": "train", "训练集": "train",
                "val": "val", "valid": "val", "validation": "val", "dev": "val", "验证": "val", "验证集": "val", "校验": "val",
                "test": "test", "testing": "test", "测试": "test", "测试集": "test"}
ANY_WORDS = {"any", "yes", "official", "has", "有", "有划分", "官方"}
NONE_WORDS = {"none", "no", "null", "无", "没有", "无划分"}
SPLIT_TEXT = re.compile(r"split|fold|hold-?out|cross-?valid|train|validation|test", re.I)
SPLIT_KEYS = re.compile(r"split|fold|cross_?valid|validation|hold_?out", re.I)


def parse_split(spec: Any, lang: str = "en") -> tuple[str, frozenset[str]] | None:
    """('any'|'none'|'parts', parts) from a --split value: any / none / train,val,test (all listed parts required)."""
    if spec in (None, "", []):
        return None
    tokens = [t.strip().casefold() for x in ([spec] if isinstance(spec, str) else list(spec)) for t in re.split(r"[,，/+]", str(x)) if t.strip()]
    if len(tokens) == 1 and tokens[0] in ANY_WORDS:
        return "any", frozenset()
    if len(tokens) == 1 and tokens[0] in NONE_WORDS:
        return "none", frozenset()
    bad = [t for t in tokens if t not in PART_ALIASES]
    if bad or not tokens:
        raise PtError(L(lang, f"cannot read split {spec!r}. Use: any (the file has an official split), none (it has none), or the parts it must "
                              "have, comma-separated: train, val, test (e.g. --split train,test). Whether the split is by patient, slide or "
                              "image is not a structured field: use --split-note patient to search the file's split-related text.",
                        f"无法解析划分条件 {spec!r}。可用：any（文件有官方划分）、none（没有），或文件必须具备的部分，逗号分隔："
                        "train、val、test（例：--split train,test）。划分是按患者、切片还是图像，不是结构化字段："
                        "请用 --split-note patient 在文件的划分相关文字里搜索。"))
    return "parts", frozenset(PART_ALIASES[t] for t in tokens)


def split_info(r: dict[str, Any]) -> dict[str, Any]:
    """What the index records about the split of one label file: parts with sample counts, samples without a split, and the source's
    own declaration (`source_label_statistics.values.split`)."""
    obs = r.get("split_distribution") or {}
    decl = (((r.get("source_label_statistics") or {}).get("values") or {}).get("split")) or {}
    parts = {k: obs[k] for k in PARTS if obs.get(k)}
    declared = {k: decl[k] for k in PARTS if decl.get(k)}
    basis = "observed"
    if not parts and declared:
        parts, basis = declared, "declared_by_source"
    return {"has_official_split": bool(parts), "parts": parts, "samples_without_split": obs.get("__missing__") or 0,
            "basis": basis if parts else None, "declared_by_source": declared or None}


def split_label(info: dict[str, Any], lang: str) -> str:
    if not info["has_official_split"]:
        return L(lang, "no official split", "无官方划分")
    names = {"train": L(lang, "train", "训练"), "val": L(lang, "val", "验证"), "test": L(lang, "test", "测试")}
    out = " · ".join(f"{names[k]} {v}" for k, v in info["parts"].items())
    if info["samples_without_split"]:
        out += L(lang, f" (no split: {info['samples_without_split']})", f"（无划分：{info['samples_without_split']}）")
    if info["basis"] == "declared_by_source":
        out += L(lang, " (counts declared by the source)", "（数量为来源声明）")
    return out


def split_notes(r: dict[str, Any]) -> list[str]:
    """The texts of a label file that speak about its split: limitations and task-schema entries (the split unit, if stated, is here)."""
    notes = [str(x) for x in (r.get("limitations") or []) if SPLIT_TEXT.search(str(x))]
    for k, v in (r.get("task_schema") or {}).items():
        if SPLIT_KEYS.search(k) and v not in (None, "", [], {}):
            txt = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
            notes.append(f"task_schema.{k}: {txt}")
    return notes


def _filter(recs: list[dict[str, Any]], level: Any, task_type: Any, task: Any, file: Any = None, split: Any = None,
            split_note: Any = None, lang: str = "en") -> list[dict[str, Any]]:
    def any_of(v: Any) -> list[str]:
        return [x.strip().casefold() for s in ([v] if isinstance(v, str) else list(v or [])) for x in str(s).split(",") if x.strip()]
    lv, tt, tk = any_of(level), any_of(task_type), any_of(task)
    sp = parse_split(split, lang)
    sn = [t.casefold() for t in any_of(split_note)]
    out = []
    for r in recs:
        if lv and str(r.get("level") or "").casefold() not in lv:
            continue
        if tt and str(r.get("task_type") or "").casefold() not in tt:
            continue
        if tk and not any(t in str(r.get("task_name") or "").casefold() for t in tk):
            continue
        if file and str(file).casefold() not in r["file"].casefold():
            continue
        if sp:
            info = split_info(r)
            if sp[0] == "any" and not info["has_official_split"]:
                continue
            if sp[0] == "none" and info["has_official_split"]:
                continue
            if sp[0] == "parts" and not sp[1] <= set(info["parts"]):
                continue
        if sn:
            text = "\n".join(split_notes(r)).casefold()
            if not any(t in text for t in sn):
                continue
        out.append(r)
    return out


def _brief(r: dict[str, Any], lang: str = "en") -> dict[str, Any]:
    info = split_info(r)
    return {"file": r["file"], "task_name": r.get("task_name"), "task_type": r.get("task_type"), "level": r.get("level"),
            "samples": r.get("total"), "size_bytes": r.get("size"), "split": split_label(info, lang),
            "has_official_split": info["has_official_split"], "split_counts": info["parts"] or None,
            "samples_without_split": info["samples_without_split"], "split_notes": split_notes(r) or None}


FILE_COLUMNS = ["file", "task_name", "task_type", "level", "samples", "size_bytes", "split"]
NOTE_MAX = 400


def _notes_block(files: list[dict[str, Any]], lang: str, indent: str = "", term: Any = None) -> list[str]:
    """Bullets with the split-related texts of the files (the split unit — patient / slide / image — is only ever stated here).
    Identical texts are listed once with the files they belong to; with a --split-note term only the texts containing it are shown."""
    terms = [t.strip().casefold() for x in ([term] if isinstance(term, str) else list(term or [])) for t in str(x).split(",") if t.strip()]
    by_text: dict[str, list[str]] = {}
    for f in files:
        for n in f.get("split_notes") or []:
            if not terms or any(t in n.casefold() for t in terms):
                by_text.setdefault(n, []).append(f["file"])
    if not by_text:
        return []
    out = [indent + L(lang, "split-related text (limitations / task schema; the split unit is only stated here, if at all):",
                      "划分相关文字（limitations / 任务结构；划分单位若有说明，只在这里）：")]
    for n, fl in list(by_text.items())[:8]:
        who = fl[0] if len(fl) == 1 else L(lang, f"{len(fl)} files, e.g. {fl[0]}", f"{len(fl)} 个文件，如 {fl[0]}")
        out.append(f"{indent}- [{who}] " + (n if len(n) <= NOTE_MAX else n[:NOTE_MAX] + "…"))
    if len(by_text) > 8:
        out.append(indent + L(lang, f"- … {len(by_text) - 8} more texts; `label get --resource ... --layer text` gives them all",
                              f"- ……还有 {len(by_text) - 8} 条；`label get --resource ... --layer text` 可看全部"))
    return out


def _index_note(lang: str) -> str:
    return L(lang, "task names, class names and the text layer come from the label files and the label index; they are shown as recorded (source-language text)",
             "任务名、类别名和文本层来自标签文件与标签索引，按记录原样给出（源语言文字，未翻译）")


def list_(data: Data, resource: Any = None, level: Any = None, task_type: Any = None, task: Any = None, offset: int = 0,
          limit: int = 30, fmt: str | None = None, output: str | None = None, where: Any = None, split: Any = None,
          split_note: Any = None) -> str:
    lang = data.lang
    env: dict[str, Any] = {"data_version": data.version, "command": "label list", "lang": lang, "notes": [_index_note(lang)]}
    conds = table.parse_where(data, where)                    # same syntax and semantics as `table search --where`
    parse_split(split, lang)                                  # validate early
    filt: dict[str, Any] = {k: v for k, v in (("level", level), ("task_type", task_type), ("task", task), ("split", split),
                                              ("split_note", split_note)) if v}
    if conds:
        filt["where"] = [c.text(lang) for c in conds]

    def res_ok(row: dict[str, Any]) -> bool:
        return all(c.matches(row, data) for c in conds)

    def files_of(row: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        recs = data.labels_by_resource.get(row["record_id"], [])
        return recs, _filter(recs, level, task_type, task, None, split, split_note, lang)

    def note_unit() -> str:
        return L(lang, "split unit: the index records which parts (train/val/test) a file has and their sample counts, not whether the split is "
                       "by patient, slide or image; if the source says so it is in the split-related text shown below (search it with "
                       "--split-note patient)",
                 "划分单位：索引记录文件有哪些部分（train/val/test）及样本数，不记录是按患者、切片还是图像划分；"
                 "来源若有说明，会出现在下面的划分相关文字里（可用 --split-note patient 搜索）")
    if resource:
        rows = data.resources(resource)
        items = []
        for r in rows:
            recs, match = files_of(r)
            ok = res_ok(r)
            if not ok:
                match = []
            files = [_brief(x, lang) for x in match]
            it = {"id": r["id"], "name": r["name"], "label_files": len(recs), "matching": len(match), "files": files}
            if not recs:
                it["note"] = L(lang, "this resource has no label file in PathTrove (most resources have none)",
                               "这个资源在 PathTrove 里没有标签文件（大多数资源都没有）")
            elif not ok:
                it["note"] = L(lang, "this resource does not satisfy the resource filters (--where)", "这个资源不满足资源过滤条件（--where）")
            items.append(it)
        env.update({"filters": filt, "items": items})
        if any(f.get("split_notes") for it in items for f in it["files"]):
            env["notes"].append(note_unit())
        body = []
        for it in items:
            body += [f"## {it['name']} ({it['id']}) — " + L(lang, f"{it['label_files']} label files", f"{it['label_files']} 个标签文件")
                     + ((L(lang, f", {it['matching']} match", f"，{it['matching']} 个匹配")) if filt else "")]
            if it.get("note"):
                body.append(it["note"])
            if it["files"]:
                body += md_table(it["files"], FILE_COLUMNS, lang)
                body += ["", *_notes_block(it["files"], lang, "", split_note)]
            body.append("")
        return emit(env, fmt, output, body, "items")
    offset, limit = int(offset), int(limit)
    if offset < 0 or limit < 1:
        raise PtError(L(lang, "--offset must be 0 or more and --limit 1 or more", "--offset 不能为负，--limit 至少为 1"))
    groups = []
    for r in (x for x in data.rows if res_ok(x)):
        recs, match = files_of(r)
        if match:
            infos = [split_info(x) for x in match]
            parts = [k for k in PARTS if any(k in i["parts"] for i in infos)]
            groups.append({"id": r["id"], "name": r["name"], "files": len(match),
                           "levels": sorted({str(x.get("level")) for x in match}),
                           "task_types": sorted({str(x.get("task_type")) for x in match}),
                           "files_with_split": sum(1 for i in infos if i["has_official_split"]),
                           "split_parts": parts or None}
                          | ({"_files": [_brief(x, lang) for x in match]} if filt else {}))
    total = len(groups)
    page = groups[offset:offset + limit]
    for g in page:                                           # with filters on, the matching files and their split detail travel with the resource
        if "_files" in g:
            g["file_list"] = g.pop("_files")
    env.update({"filters": filt, "resources_with_matching_labels": total, "offset": offset, "limit": limit, "items": page})
    if total == 0:
        env["notes"].append(L(lang, "0 resources have label files matching the filters (label levels/types: run `label list` without filters)",
                              "没有资源的标签文件匹配这些过滤条件（想看有哪些层级/类型：不加过滤运行 `label list`）"))
    if total > offset + limit:
        env["next"] = f"--offset {offset + limit}"
    if any(f.get("split_notes") for g in page for f in g.get("file_list", [])):
        env["notes"].append(note_unit())
    body = [L(lang, f"{total} resources have matching label files" + (f" (showing {offset + 1}–{offset + len(page)})" if page else ""),
              f"{total} 个资源有匹配的标签文件" + (f"（显示第 {offset + 1}–{offset + len(page)} 个）" if page else ""))]
    if filt:
        shown = [f"{k}={v}" for k, v in filt.items() if k != "where"] + list(filt.get("where", []))
        body[0] += L(lang, "; filters: ", "；过滤条件：") + ", ".join(shown)
    if page:
        body += ["", *md_table([{k: v for k, v in g.items() if k != "file_list"} for g in page], None, lang)]
        if filt:                                             # with filters on, list the matching files with their split parts and counts
            for g in page:
                body += ["", f"### {g['name']} ({g['id']})", *md_table(g["file_list"][:6], FILE_COLUMNS, lang)]
                if len(g["file_list"]) > 6:
                    body.append(L(lang, f"… {len(g['file_list']) - 6} more files: `label list --resource \"{g['name']}\"`",
                                  f"……还有 {len(g['file_list']) - 6} 个文件：`label list --resource \"{g['name']}\"`"))
                body += _notes_block(g["file_list"], lang, "", split_note)
        else:
            body += ["", L(lang, "split_parts / files_with_split: parts (train/val/test) and number of files that have an official split; "
                                 "add a filter (--where, --split, --level ...) to list the files with their split counts",
                           "split_parts / files_with_split：划分部分（train/val/test）和有官方划分的文件数；"
                           "加过滤条件（--where、--split、--level ……）可列出各文件及其划分数量")]
    if env.get("next"):
        body.append(L(lang, f"\nmore: {env['next']}", f"\n下一页：{env['next']}"))
    return emit(env, fmt, output, body, "items")


def get(data: Data, resource: Any, file: Any = None, level: Any = None, task_type: Any = None, task: Any = None, split: Any = None,
        layer: Any = None, max_classes: int = 30, fmt: str | None = None, output: str | None = None) -> str:
    lang = data.lang
    rows = data.resources(resource)
    layers = parse_layers(layer, ("value",), lang)
    max_classes = int(max_classes)
    sp = parse_split(split, lang)
    items, notes = [], [_index_note(lang)]
    for r in rows:
        recs = data.labels_by_resource.get(r["record_id"], [])
        match = _filter(recs, level, task_type, task, file, split, None, lang)
        it: dict[str, Any] = {"id": r["id"], "name": r["name"], "label_files": len(recs), "matching": len(match), "labels": []}
        if not recs:
            it["note"] = L(lang, "this resource has no label file in PathTrove", "这个资源在 PathTrove 里没有标签文件")
        for x in match:
            e: dict[str, Any] = {"file": x["file"]}
            if "value" in layers:
                cd = x.get("class_distribution") or {}
                top = sorted(cd.items(), key=lambda kv: -kv[1] if isinstance(kv[1], (int, float)) else 0)
                schema = x.get("task_schema") or {}
                declared = ((x.get("source_label_statistics") or {}).get("values") or {}).get("total")
                e["value"] = {"task_name": x.get("task_name"), "task_type": x.get("task_type"), "level": x.get("level"),
                              "samples_observed": x.get("total"), "samples_declared_by_source": declared,
                              "n_classes": len(cd) or None,
                              "class_distribution": dict(top[:max_classes]) or None,
                              "class_names": schema.get("class_names"),
                              "split_distribution": x.get("split_distribution"),
                              "raw_file": {"size_bytes": x.get("size"), "sha256": x.get("sha256"), "fetch": "label fetch"}}
                if len(top) > max_classes:
                    e["value"]["class_distribution_note"] = L(lang, f"top {max_classes} of {len(top)} classes shown; raise --max-classes",
                                                              f"只显示 {len(top)} 个类别中的前 {max_classes} 个；请加大 --max-classes")
                e["value"]["split"] = split_label(split_info(x), lang)
                if sp and sp[0] == "parts":
                    e["value"]["split_distribution"] = {k: v for k, v in (x.get("split_distribution") or {}).items() if k in sp[1]}
            if "text" in layers:
                e["text"] = {"task_schema": x.get("task_schema"), "limitations": x.get("limitations")}
            if "source" in layers:
                e["source"] = {"class_distribution_basis": x.get("class_distribution_basis"),
                               "provenance": x.get("source_provenance")}
            it["labels"].append(e)
        if recs and not match:
            it["note"] = L(lang, f"none of its {len(recs)} label files match the filters; `label list --resource ...` shows them",
                           f"它的 {len(recs)} 个标签文件都不匹配过滤条件；`label list --resource ...` 可列出它们")
        items.append(it)
    env = {"data_version": data.version, "command": "label get", "lang": lang, "layers": list(layers), "notes": notes, "items": items,
           "reading": [L(lang, "samples_observed = samples counted when the label index was built; samples_declared_by_source = the count the source "
                               "states (they can differ); class and split counts are recomputed from the observed samples; "
                               "split '__missing__' = samples without a split",
                         "samples_observed = 建标签索引时统计到的样本数；samples_declared_by_source = 来源自己声明的数量（两者可能不同）；"
                         "类别和划分的数量按统计到的样本重新计算；划分 '__missing__' = 没有划分的样本")]}
    body = []
    for it in items:
        body.append(f"## {it['name']} ({it['id']}) — " + L(lang, f"{it['label_files']} label files, {it['matching']} shown",
                                                            f"{it['label_files']} 个标签文件，显示 {it['matching']} 个"))
        if it.get("note"):
            body.append(it["note"])
        for e in it["labels"]:
            body += [f"### {e['file']}", *md_lines({k: v for k, v in e.items() if k != "file"}, 0, lang)]
        body.append("")
    return emit(env, fmt, output, body, "items")


# ---------------------------------------------------------------- fetch

def download(data: Data, rec: dict[str, Any], dest: Path) -> str:
    lang = data.lang
    repo = data.manifest["labels"]["hf_repo"]
    url = net.hf_url(repo, rec["repo_path"])
    got = net.download(url, dest, rec["file"], rec["size"], rec["sha256"], lang, rec["file"])
    if got["already_present"]:
        return L(lang, f"already present and verified: {got['path']}\nsize {rec['size']} bytes, sha256 {rec['sha256']}",
                 f"已存在且校验通过：{got['path']}\n大小 {rec['size']} 字节，sha256 {rec['sha256']}")
    return L(lang, f"saved and verified: {got['path']}\nsize {got['size']} bytes, sha256 {rec['sha256']} (matches the data manifest)\nsource {url}",
             f"已保存并校验：{got['path']}\n大小 {got['size']} 字节，sha256 {rec['sha256']}（与数据清单一致）\n来源 {url}")


def fetch(data: Data, resource: Any, dest: str | None, file: Any = None, fmt: str | None = None, output: str | None = None) -> str:
    lang = data.lang
    if not dest:
        raise PtError(L(lang, "--dest DIR (target directory) is required", "必须给出 --dest 目录（保存位置）"))
    rows = data.resources(resource)
    if len(rows) != 1:
        raise PtError(L(lang, "label fetch takes exactly one resource", "label fetch 每次只能给一个资源"))
    r = rows[0]
    recs = [x for x in data.labels_by_resource.get(r["record_id"], []) if x.get("repo_path")]
    head = f"[PathTrove {L(lang, 'data', '数据')} {data.version} · label fetch]"
    if not recs:
        return head + "\n" + L(lang, f"nothing downloaded: {r['name']} has no label file in PathTrove", f"未下载任何文件：{r['name']} 在 PathTrove 里没有标签文件") + "\n"
    hit = _filter(recs, None, None, None, file) if file else recs
    exact = [x for x in hit if file and x["file"] == file]
    hit = exact or hit
    listing = "\n".join(f"  {x['file']}  {x['size'] / 1e6:.1f} MB  ({x.get('task_type')}, {x.get('level')})" for x in hit or recs)
    if not hit:
        return head + "\n" + L(lang, f"nothing downloaded: no file matching {file!r}. Files of {r['name']}:\n{listing}",
                              f"未下载任何文件：没有匹配 {file!r} 的文件。{r['name']} 的文件：\n{listing}") + "\n"
    if len(hit) > 1:
        return head + "\n" + L(lang, f"nothing downloaded: {len(hit)} files match; choose one with --file (full name):\n{listing}",
                              f"未下载任何文件：有 {len(hit)} 个文件匹配；请用 --file 指定其一（完整文件名）：\n{listing}") + "\n"
    return f"{head}\n{download(data, hit[0], Path(dest).expanduser())}\n"
