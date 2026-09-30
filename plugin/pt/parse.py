"""Reports and download guides: split into fields (value / text / source) and sections."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

FIELD = re.compile(r"^- \*\*(\d+)\. [^\n]*?\*\*:(.*?)(?=^- \*\*\d+\. |^## |\Z)", re.S | re.M)
JSON_BLOCK = re.compile(r"[ \t]*```json\n(.*?)\n[ \t]*```", re.S)
SOURCE_LINE = re.compile(r"^\s*>\s*(?:来源|Source)\s*[:：]\s*(.*)$")
FENCE = re.compile(r"^\s*```")

# One set of section names for both guide templates and both languages. First substring hit wins,
# so longer headings come first.
SECTION_RULES = [
    ("图像与 metadata 对应关系", "correspondence"), ("image–metadata correspondence", "correspondence"),
    ("image-metadata correspondence", "correspondence"), ("下载后检查", "post_checks"), ("post-download check", "post_checks"),
    ("权限、许可证和网络限制", "access"), ("access, license and network", "access"), ("注意事项", "access"),
    ("访问与合规提示", "access"), ("核验依据", "evidence"), ("verification evidence", "evidence"),
    ("复测", "retest"), ("retest", "retest"), ("re-test", "retest"),
    ("结论", "conclusion"), ("conclusion", "conclusion"), ("下载步骤", "steps"), ("download steps", "steps"),
    ("下载病理图像", "main_data"), ("pathology images", "main_data"), ("下载对象", "objects"), ("download objects", "objects"),
    ("前置条件", "prerequisites"), ("prerequisites", "prerequisites"), ("metadata", "metadata"),
    ("附录", "appendix"), ("appendix", "appendix"),
]
SECTION_ORDER = ["conclusion", "objects", "prerequisites", "metadata", "main_data", "steps", "correspondence",
                 "post_checks", "access", "evidence", "retest", "appendix", "other"]
SECTION_HELP = {
    "conclusion": "download conclusion (old template only)", "objects": "what can be downloaded, in a table",
    "prerequisites": "accounts, tools, network (new template)", "metadata": "how to get the metadata / annotations",
    "main_data": "how to get the images / main data", "steps": "download steps (old template)",
    "correspondence": "how images map to metadata (new template)", "post_checks": "checks after downloading (new template)",
    "access": "permissions, license, network limits (old: notes)", "evidence": "what the guide was verified against",
    "retest": "later re-tests", "appendix": "appendix",
}


def unify(heading: str) -> str:
    h = re.sub(r"^\d+(\.\d+)*\.?\s*", "", heading).strip().casefold()
    for needle, name in SECTION_RULES:
        if needle.casefold() in h:
            return name
    return "other"


def load_json_lenient(text: str) -> tuple[Any, str | None]:
    """Parse a JSON block. Some reports were written with curly quotes; retry with them replaced, and say so."""
    try:
        return json.loads(text), None
    except ValueError:
        pass
    fixed = text.replace("“", '"').replace("”", '"')
    try:
        return json.loads(fixed), "block is not valid JSON as written (curly quotes); parsed after replacing them with straight quotes"
    except ValueError as err:
        return None, f"block is not valid JSON ({err}); raw text kept in value_raw"


@lru_cache(maxsize=64)
def parse_report(path: str) -> dict[int, dict[str, Any]]:
    """{field id: {value, value_note, value_raw, text, source[]}} for the numbered fields of a report."""
    text = Path(path).read_text(encoding="utf-8")
    out: dict[int, dict[str, Any]] = {}
    for m in FIELD.finditer(text):
        fid, chunk = int(m.group(1)), m.group(2)
        jm = JSON_BLOCK.search(chunk)
        value = note = raw = None
        if jm:
            raw = jm.group(1)
            value, note = load_json_lenient(raw)
            rest = chunk[:jm.start()] + chunk[jm.end():]
        else:
            rest = chunk
        source, body = [], []
        for ln in rest.splitlines():
            sm = SOURCE_LINE.match(ln)
            if sm:
                source.append(sm.group(1).strip())
            else:
                body.append(ln)
        out[fid] = {"value": value, "value_note": note, "value_raw": raw if (jm and value is None) else None,
                    "has_value_block": bool(jm), "text": "\n".join(body).strip() or None, "source": source}
    return out


@lru_cache(maxsize=64)
def parse_guide(path: str) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    m = re.match(r"\s*```json\n(.*?)\n```\s*", text, re.S)
    block, body = None, text
    if m:
        block, _ = load_json_lenient(m.group(1))
        body = text[m.end():]
    sections, cur, fence = [], None, False
    for line in body.splitlines():
        if FENCE.match(line):
            fence = not fence
        if not fence and line.startswith("## "):
            cur = {"heading": line[3:].strip(), "lines": []}
            cur["name"] = unify(cur["heading"])
            sections.append(cur)
        elif cur is not None:
            cur["lines"].append(line)
    for s in sections:
        s["text"] = "\n".join(s.pop("lines")).strip()
    names = {s["name"] for s in sections}
    template = ("new" if names & {"prerequisites", "main_data", "correspondence"}
                else "old" if names & {"conclusion", "steps"} else "unknown")
    dv = block.get("download_verification") if isinstance(block, dict) else None
    schema = ("download_verification" if dv is not None
              else "3.0" if isinstance(block, dict) and block.get("schema_version") == "3.0" else "none")
    return {"block": block, "dv": dv, "schema": schema, "sections": sections, "template": template}
