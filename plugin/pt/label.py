"""label domain: which label files a resource has, what they contain (from the bundled index), and fetching the raw file."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from . import net
from .data import Data
from .errors import PtError
from .i18n import L
from .render import emit, md_lines, md_table, parse_layers


def _filter(recs: list[dict[str, Any]], level: Any, task_type: Any, task: Any, file: Any = None, split: Any = None) -> list[dict[str, Any]]:
    def any_of(v: Any) -> list[str]:
        return [x.strip().casefold() for s in ([v] if isinstance(v, str) else list(v or [])) for x in str(s).split(",") if x.strip()]
    lv, tt, tk = any_of(level), any_of(task_type), any_of(task)
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
        if split and not any(str(split).casefold() == k.casefold() and v not in (None, 0) for k, v in (r.get("split_distribution") or {}).items()):
            continue
        out.append(r)
    return out


def _brief(r: dict[str, Any]) -> dict[str, Any]:
    return {"file": r["file"], "task_name": r.get("task_name"), "task_type": r.get("task_type"), "level": r.get("level"),
            "samples": r.get("total"), "size_bytes": r.get("size")}


def _index_note(lang: str) -> str:
    return L(lang, "task names, class names and the text layer come from the label files and the label index; they are shown as recorded (source-language text)",
             "任务名、类别名和文本层来自标签文件与标签索引，按记录原样给出（源语言文字，未翻译）")


def list_(data: Data, resource: Any = None, level: Any = None, task_type: Any = None, task: Any = None, offset: int = 0,
          limit: int = 30, fmt: str | None = None, output: str | None = None) -> str:
    lang = data.lang
    env: dict[str, Any] = {"data_version": data.version, "command": "label list", "lang": lang, "notes": [_index_note(lang)]}
    filt = {k: v for k, v in (("level", level), ("task_type", task_type), ("task", task)) if v}
    if resource:
        rows = data.resources(resource)
        items = []
        for r in rows:
            recs = data.labels_by_resource.get(r["id"], [])
            match = _filter(recs, level, task_type, task)
            it = {"id": r["id"], "name": r["name"], "label_files": len(recs), "matching": len(match), "files": [_brief(x) for x in match]}
            if not recs:
                it["note"] = L(lang, "this resource has no label file in PathTrove (most resources have none)",
                               "这个资源在 PathTrove 里没有标签文件（大多数资源都没有）")
            items.append(it)
        env.update({"filters": filt, "items": items})
        body = []
        for it in items:
            body += [f"## {it['name']} ({it['id']}) — " + L(lang, f"{it['label_files']} label files", f"{it['label_files']} 个标签文件")
                     + ((L(lang, f", {it['matching']} match", f"，{it['matching']} 个匹配")) if filt else "")]
            if it.get("note"):
                body.append(it["note"])
            if it["files"]:
                body += md_table(it["files"], None, lang)
            body.append("")
        return emit(env, fmt, output, body, "items")
    offset, limit = int(offset), int(limit)
    groups = []
    for r in data.rows:
        recs = data.labels_by_resource.get(r["id"], [])
        match = _filter(recs, level, task_type, task)
        if match:
            groups.append({"id": r["id"], "name": r["name"], "files": len(match),
                           "levels": sorted({str(x.get("level")) for x in match}),
                           "task_types": sorted({str(x.get("task_type")) for x in match})})
    total = len(groups)
    page = groups[offset:offset + limit]
    env.update({"filters": filt, "resources_with_matching_labels": total, "offset": offset, "limit": limit, "items": page})
    if total == 0:
        env["notes"].append(L(lang, "0 resources have label files matching the filters (label levels/types: run `label list` without filters)",
                              "没有资源的标签文件匹配这些过滤条件（想看有哪些层级/类型：不加过滤运行 `label list`）"))
    if total > offset + limit:
        env["next"] = f"--offset {offset + limit}"
    body = [L(lang, f"{total} resources have matching label files" + (f" (showing {offset + 1}–{offset + len(page)})" if page else ""),
              f"{total} 个资源有匹配的标签文件" + (f"（显示第 {offset + 1}–{offset + len(page)} 个）" if page else ""))]
    if page:
        body += ["", *md_table(page, None, lang)]
    if env.get("next"):
        body.append(L(lang, f"\nmore: {env['next']}", f"\n下一页：{env['next']}"))
    return emit(env, fmt, output, body, "items")


def get(data: Data, resource: Any, file: Any = None, level: Any = None, task_type: Any = None, task: Any = None, split: Any = None,
        layer: Any = None, max_classes: int = 30, fmt: str | None = None, output: str | None = None) -> str:
    lang = data.lang
    rows = data.resources(resource)
    layers = parse_layers(layer, ("value",), lang)
    max_classes = int(max_classes)
    items, notes = [], [_index_note(lang)]
    for r in rows:
        recs = data.labels_by_resource.get(r["id"], [])
        match = _filter(recs, level, task_type, task, file, split)
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
                if split:
                    e["value"]["split_distribution"] = {k: v for k, v in (x.get("split_distribution") or {}).items()
                                                        if k.casefold() == str(split).casefold()}
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
    recs = [x for x in data.labels_by_resource.get(r["id"], []) if x.get("repo_path")]
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
