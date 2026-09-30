"""The data package: resource table (Chinese and English), field catalogue, name resolution, file locations.

`Data(lang)` is a view of the unpacked package in one language; the package itself is loaded once (Core).
"""
from __future__ import annotations

import difflib
import json
import re
import unicodedata
from functools import cached_property
from pathlib import Path
from typing import Any

from . import store
from .errors import PtError
from .i18n import L, norm_lang

# English names of the 38 report fields (translate/PROMPT.md, "Report fields"; they match the English PathTrove table).
FIELD_EN = {
    1: "Dataset Name", 2: "Dataset Homepage", 3: "Openness", 4: "Open Source & Access Notes", 5: "Release Date",
    6: "Organ", 7: "Staining", 8: "Tumor Types", 9: "Data Modality", 10: "Data Details",
    11: "Cohort Diversity & Multi-Center Distribution", 12: "Rare Disease Status", 13: "Rare Disease Names",
    14: "Data Volume", 15: "Storage Size", 16: "Image Count", 17: "Digital Slide Format",
    18: "Tissue Preparation Format", 19: "Scanner Information", 20: "Demographics & Bias",
    21: "QC Status & QC Aspects", 22: "Spatial Transcriptomics Resolution", 23: "Task Tags",
    24: "Image Data Source", 25: "Annotation Data Source", 26: "Task Description", 27: "Image Alignment Quality",
    28: "Paper Title", 29: "Paper Homepage", 30: "Download URL", 31: "Citations (BibTeX)", 32: "License",
    33: "Remarks", 34: "Paper Citations & GitHub Stars", 35: "Source Provenance", 36: "Data Type",
    37: "Primary Taxonomy Fields", 38: "Clinical Metadata",
}
# English names of the columns, where they differ from the field name (fields with more than one column).
COLUMN_EN = {
    "7-2": "Stain Markers", "8-2": "Disease Context", "10-1": "Overview", "10-2": "Data Details",
    "11-1": "Center Type", "11-2": "Cohort Diversity Notes", "16-2": "Image Count Unit", "16-3": "Image Count Notes",
    "17-2": "Digital Slide Format Notes", "19-1": "Scanner Vendor/Model", "19-2": "Scanner Notes",
    "21-2": "QC Aspects", "21-3": "QC Notes", "24-2": "Image Source Details", "25-2": "Annotation Source Details",
    "27-2": "Alignment Target", "27-3": "Alignment Notes", "34-1": "Paper Citations", "34-2": "GitHub Stars",
    "9-1": "Data Labels", "12-1": "Rare Diseases", "23-1": "Task Tags", "36-1": "Type", "4-1": "Open Access Notes",
}
# Free-text columns that hold a short value (a name or a delimited list) rather than prose.
SHORT_TEXT = {"1-1", "7-2", "8-1", "19-1", "27-2", "28-1"}
# Columns of the table that are attachments or internal, not report fields.
INTERNAL_COLUMNS = {"报告附件", "下载指南", "label.json"}
NAME_COLUMN = "数据集名称"
LINK = re.compile(r"\((https?://[^)\s]+)\)")


def norm(text: str) -> str:
    """NFKC + casefold + drop everything that is not a letter or digit."""
    return "".join(ch for ch in unicodedata.normalize("NFKC", str(text)).casefold() if ch.isalnum())


def suggest(word: str, options: list[str], n: int = 5) -> list[str]:
    keyed = {norm(o): o for o in options}
    hits = difflib.get_close_matches(norm(word), list(keyed), n=n, cutoff=0.5)
    sub = [k for k in keyed if norm(word) and norm(word) in k and k not in hits]
    return [keyed[k] for k in hits + sub][:n]


class Column:
    def __init__(self, field_id: int, col: dict[str, Any], field_zh: str, field_en: str, sample: list[Any]):
        self.field_id, self.id, self.zh = field_id, col["id"], col["name"]
        self.field_zh, self.field_en = field_zh, field_en
        self.en = COLUMN_EN.get(col["id"]) or field_en
        self.declared = col.get("type")
        self.enum = col.get("enum_values") or []
        non_null = [v for v in sample if v not in (None, [], "")]
        if any(isinstance(v, list) for v in non_null) or col["type"] == "categorical":
            self.kind = "categorical"
        elif any(isinstance(v, (int, float)) and not isinstance(v, bool) for v in non_null) or col["type"] == "numeric":
            self.kind = "numeric"
        elif col["type"] == "date":
            self.kind = "date"
        elif col["type"] == "link":
            self.kind = "link"
        else:
            self.kind = "short" if col["id"] in SHORT_TEXT else "text"

    @property
    def is_value(self) -> bool:
        """Does the column carry a structured value (as opposed to prose)?"""
        return self.kind != "text"

    def name(self, lang: str) -> str:
        return self.en if lang == "en" else self.zh

    def label(self, lang: str = "en") -> str:
        return f"{self.id} {self.name(lang)}"

    def value(self, row: dict[str, Any]) -> Any:
        raw = row["fields"].get(self.zh)
        if raw in (None, "", []):
            return None
        if self.kind == "categorical":
            return [str(x) for x in raw] if isinstance(raw, list) else [str(raw)]
        if self.kind == "link":
            urls = LINK.findall(raw) if isinstance(raw, str) else []
            return urls or ([raw] if isinstance(raw, str) else None)
        return raw


class Core:
    """The unpacked data package, loaded once per process and shared by the per-language views."""
    _cache: dict[str, "Core"] = {}

    @classmethod
    def get(cls, root: Path) -> "Core":
        key = str(root)
        if key not in cls._cache:
            cls._cache[key] = cls(root)
        return cls._cache[key]

    def __init__(self, root: Path):
        self.root = root

    @cached_property
    def manifest(self) -> dict[str, Any]:
        """The plugin manifest: version, counts, limitations, label file list, translation coverage."""
        return store.plugin_manifest()

    @cached_property
    def rows(self) -> list[dict[str, Any]]:
        rows = json.loads((self.root / "table_snapshot.json").read_text(encoding="utf-8"))["rows"]
        for r in rows:
            r["id"] = r["record_id"]
            r["name"] = str(r["fields"].get(NAME_COLUMN) or r["record_id"])
        return rows

    @cached_property
    def en_snapshot(self) -> dict[str, Any] | None:
        p = self.root / "table_snapshot_en.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    @cached_property
    def rows_en(self) -> list[dict[str, Any]]:
        """The English table aligned to the Chinese one by record id, with values stored under the Chinese column names so that
        every column lookup works in both languages. A record missing from the English table keeps its Chinese row, flagged."""
        snap = self.en_snapshot
        if snap is None:
            raise PtError("this data package has no English table (table_snapshot_en.json); use lang=zh / 数据包没有英文表，请用 lang=zh")
        by = {r["record_id"]: r for r in snap["rows"]}
        cmap = snap["column_map"]
        out = []
        for zr in self.rows:
            er = by.get(zr["id"])
            if er is None:
                out.append({**zr, "lang_fallback": True})
                continue
            fields = {zh: er["fields"].get(en) for zh, en in cmap.items()}
            for col in INTERNAL_COLUMNS:                       # attachments are files, not language-dependent cells
                fields[col] = zr["fields"].get(col)
            out.append({"record_id": zr["id"], "id": zr["id"], "fields": fields,
                        "name": str(er["fields"].get("Dataset Name") or zr["name"])})
        return out

    @cached_property
    def value_map(self) -> dict[str, dict[str, str]]:
        """{column id: {Chinese value: English value}} for categorical columns whose two spellings differ."""
        return (self.en_snapshot or {}).get("value_map", {})

    @cached_property
    def label_records(self) -> list[dict[str, Any]]:
        """Label index records joined with the manifest's label file list (record id, file name, size, sha256)."""
        index = json.loads((self.root / "label_index.json").read_text(encoding="utf-8"))["records"]
        files = {f["name"]: f for f in (self.manifest.get("labels") or {}).get("files", [])}
        out = []
        for rec in index:
            fname = Path(rec["source_path"]).name
            f = files.get(fname)
            out.append({**rec, "file": fname, "record_id": f["record_id"] if f else None,
                        "size": f["size"] if f else None, "sha256": f["sha256"] if f else None,
                        "repo_path": f["path"] if f else None})
        return out

    @cached_property
    def labels_by_resource(self) -> dict[str, list[dict[str, Any]]]:
        out: dict[str, list[dict[str, Any]]] = {}
        for rec in self.label_records:
            if rec["record_id"]:
                out.setdefault(rec["record_id"], []).append(rec)
        return out

    @cached_property
    def columns(self) -> list[Column]:
        catalog = json.loads((self.root / "report_fields.json").read_text(encoding="utf-8"))
        cols = []
        for fid_s, fd in catalog.items():
            fid = int(fid_s)
            for c in fd["columns"]:
                sample = [r["fields"].get(c["name"]) for r in self.rows]
                cols.append(Column(fid, c, fd["name_zh"], FIELD_EN.get(fid, fd["name_en"]), sample))
        return sorted(cols, key=lambda c: tuple(int(p) for p in c.id.split("-")))

    @cached_property
    def field_zh(self) -> dict[int, str]:
        catalog = json.loads((self.root / "report_fields.json").read_text(encoding="utf-8"))
        zh = {int(k): v["name_zh"] for k, v in catalog.items()}
        zh.setdefault(13, "罕见病名称")
        return zh


class Data:
    """The data package in one language (`lang` zh or en; default PATHTROVE_LANG, else zh)."""

    def __init__(self, lang: str | None = None, root: Path | None = None):
        self.lang = norm_lang(lang)
        self.root = Path(root) if root else store.ensure_data(self.lang)
        self.core = Core.get(self.root)
        self.bundle = self.root

    def in_lang(self, lang: str | None) -> "Data":
        lang = norm_lang(lang) if lang else self.lang
        return self if lang == self.lang else Data(lang, self.root)

    # ------------------------------------------------------------ loading
    @property
    def manifest(self) -> dict[str, Any]:
        return self.core.manifest

    @property
    def version(self) -> str:
        return self.manifest["data_version"]

    @cached_property
    def rows(self) -> list[dict[str, Any]]:
        return self.core.rows_en if self.lang == "en" else self.core.rows

    @cached_property
    def by_id(self) -> dict[str, dict[str, Any]]:
        return {r["id"]: r for r in self.rows}

    @property
    def label_records(self) -> list[dict[str, Any]]:
        return self.core.label_records

    @property
    def labels_by_resource(self) -> dict[str, list[dict[str, Any]]]:
        return self.core.labels_by_resource

    # ------------------------------------------------------------ field catalogue
    @property
    def columns(self) -> list[Column]:
        return self.core.columns

    @cached_property
    def field_ids(self) -> list[int]:
        return sorted(FIELD_EN)

    @property
    def field_zh(self) -> dict[int, str]:
        return self.core.field_zh

    def field_name(self, fid: int, lang: str | None = None) -> str:
        lang = lang or self.lang
        return FIELD_EN[fid] if lang == "en" else self.field_zh.get(fid, FIELD_EN[fid])

    @cached_property
    def _column_aliases(self) -> dict[str, Column]:
        aliases: dict[str, Column] = {}
        for c in self.columns:
            for a in (c.id, c.zh, c.en, c.field_zh, c.field_en, str(c.field_id) if c.id.endswith("-1") else None):
                if a:
                    aliases.setdefault(norm(a), c)
        for c in self.columns:                      # exact column names beat field names
            aliases[norm(c.id)] = c
            aliases[norm(c.zh)] = c
            aliases[norm(c.en)] = c
        return aliases

    @cached_property
    def _field_aliases(self) -> dict[str, int]:
        aliases: dict[str, int] = {}
        for fid in self.field_ids:
            for a in (str(fid), self.field_zh.get(fid), FIELD_EN[fid]):
                if a:
                    aliases[norm(a)] = fid
        for c in self.columns:                      # a column name also names its field
            aliases.setdefault(norm(c.zh), c.field_id)
            aliases.setdefault(norm(c.en), c.field_id)
        for c in self.columns:                      # column ids like "7-2" name their field too
            aliases.setdefault(norm(c.id), c.field_id)
        return aliases

    def names_in_lang(self) -> list[str]:
        return [x.name(self.lang) for x in self.columns]

    def _near_columns(self, token: str) -> list[str]:
        """Names (in the call's language) of the columns whose id, Chinese or English name is close to the token."""
        keyed = {k: c for k, c in self._column_aliases.items()}
        hits = difflib.get_close_matches(norm(token), list(keyed), n=8, cutoff=0.5)
        sub = [k for k in keyed if norm(token) and norm(token) in k and k not in hits]
        out: list[str] = []
        for k in hits + sub:
            n = keyed[k].name(self.lang)
            if n not in out:
                out.append(n)
        return out[:5]

    def column(self, token: str) -> Column:
        """A table column by field id, column id ('7-2'), Chinese or English name (case, spaces and underscores do not matter).
        A field with several columns resolves to its first one."""
        c = self._column_aliases.get(norm(token))
        if c is None:
            hint = self._near_columns(token)
            raise PtError(L(self.lang,
                            f"no table field {token!r}. " + (f"Did you mean: {', '.join(hint)}? " if hint else "")
                            + "Run `table fields` for the catalogue (ids, Chinese and English names).",
                            f"没有表格字段 {token!r}。" + (f"你是不是想找：{'、'.join(hint)}？" if hint else "")
                            + "运行 `table fields` 查看字段目录（编号、中文名、英文名）。"))
        return c

    def field_id(self, token: str, what: str = "report field") -> int:
        fid = self._field_aliases.get(norm(token))
        if fid is None:
            hint = []
            for k in difflib.get_close_matches(norm(token), list(self._field_aliases), n=8, cutoff=0.5) + \
                    [k for k in self._field_aliases if norm(token) and norm(token) in k]:
                n = self.field_name(self._field_aliases[k])
                if n not in hint:
                    hint.append(n)
            hint = hint[:5]
            what_zh = {"report field": "报告字段", "table field": "表格字段"}.get(what, what)
            raise PtError(L(self.lang,
                            f"no {what} {token!r}. " + (f"Did you mean: {', '.join(hint)}? " if hint else "")
                            + "Fields are given by id (1-38), Chinese or English name; run `table fields`.",
                            f"没有{what_zh} {token!r}。" + (f"你是不是想找：{'、'.join(hint)}？" if hint else "")
                            + "字段可用编号（1-38）、中文名或英文名指定；运行 `table fields` 查看。"))
        return fid

    def field_ids_from(self, spec: Any) -> list[int]:
        tokens = [t.strip() for s in ([spec] if isinstance(spec, str) else spec or []) for t in str(s).split(",") if t.strip()]
        if any(norm(t) == "all" for t in tokens):
            return list(self.field_ids)
        out = [self.field_id(t) for t in tokens]
        return list(dict.fromkeys(out))

    # ------------------------------------------------------------ categorical values in either language
    def value_in_lang(self, col: Any, value: str) -> str | None:
        """Translate a categorical value given in the other language into this call's language; None if it has no mapping."""
        vm = self.core.value_map.get(getattr(col, "id", ""), {})
        if self.lang == "en":
            return vm.get(value)
        rev = {en: zh for zh, en in vm.items()}
        return rev.get(value)

    # ------------------------------------------------------------ resources
    def resolve(self, key: str) -> list[dict[str, Any]]:
        key = key.strip()
        if key in self.by_id:
            return [self.by_id[key]]
        exact = [r for r in self.rows if r["name"].casefold() == key.casefold()]
        if exact:
            return exact
        n = norm(key)
        loose = [r for r in self.rows if norm(r["name"]) == n] if n else []
        if loose:
            return loose
        return [r for r in self.rows if n and n in norm(r["name"])]

    def resources(self, spec: Any) -> list[dict[str, Any]]:
        """Resolve names or record ids (a list, or a string with comma-separated entries) to table rows.
        Ambiguous or unknown names are errors that list the candidates."""
        items = [spec] if isinstance(spec, str) else list(spec or [])
        need = L(self.lang, "give a resource: --resource NAME (dataset name or record id; repeat or comma-separate for several)",
                 "请给出资源：--resource 名称（数据集名称或 record id；可重复或用逗号分隔多个）")
        if not items:
            raise PtError(need)
        keys: list[str] = []
        for it in items:
            it = str(it).strip()
            if self.resolve(it):
                keys.append(it)                       # names may contain commas: try the whole entry first
            else:
                keys += [p.strip() for p in it.split(",") if p.strip()]
        if not keys:
            raise PtError(need)
        out, seen = [], set()
        for k in keys:
            hits = self.resolve(k)
            if not hits:
                near = suggest(k, [r["name"] for r in self.rows])
                raise PtError(L(self.lang,
                                f"no resource matches {k!r} in PathTrove {self.version}. "
                                + (f"Near matches: {'; '.join(near)}. " if near else "")
                                + "Not found here does not mean it does not exist; try `table search --query ...`.",
                                f"PathTrove {self.version} 中没有与 {k!r} 匹配的资源。"
                                + (f"相近的有：{'；'.join(near)}。" if near else "")
                                + "这里没找到不等于它不存在；可试试 `table search --query ...`。"))
            if len(hits) > 1:
                cand = "; ".join(f"{h['name']} ({h['id']})" for h in hits[:12])
                raise PtError(L(self.lang, f"{k!r} matches {len(hits)} resources: {cand}. Give the exact name or the record id.",
                                f"{k!r} 匹配到 {len(hits)} 个资源：{cand}。请给出完整名称或 record id。"))
            if hits[0]["id"] not in seen:
                seen.add(hits[0]["id"])
                out.append(hits[0])
        return out

    # ------------------------------------------------------------ files
    def report_path(self, row: dict[str, Any], lang: str | None = None) -> Path | None:
        lang = lang or self.lang
        if lang == "en":
            p = self.root / "en" / "reports" / f"{row['id']}.md"
            return p if p.exists() else None
        att = row["fields"].get("报告附件") or []
        if not att:
            return None
        stem = att[0]["name"].removesuffix(".md")
        for name in (f"{stem}.md", f"{stem}__{row['id']}.md"):
            if (self.root / "reports" / name).exists():
                return self.root / "reports" / name
        return None

    def guide_path(self, row: dict[str, Any], lang: str | None = None) -> Path | None:
        lang = lang or self.lang
        if lang == "en":
            p = self.root / "en" / "guides" / f"{row['id']}.md"
            return p if p.exists() else None
        dup = sum(1 for r in self.core.rows if r["name"] == row["name"]) > 1
        safe = re.sub(r'[/\\:*?"<>|]+', "_", row["name"]).strip() or "unnamed"
        folder = self.root / "download_guides" / (f"{safe}__{row['id']}" if dup else safe)
        files = sorted(folder.glob("*.md")) if folder.exists() else []
        return files[0] if len(files) == 1 else None

    def rel(self, path: Path) -> str:
        return str(path.relative_to(self.root))
