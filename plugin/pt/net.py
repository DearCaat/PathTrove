"""Downloads over HTTP(S) with the standard library: redirects (including 308), resume, size and sha256 verification.

Used for the data archive and for raw label files. The host is `HF_ENDPOINT` (default https://huggingface.co), so a mirror
such as https://hf-mirror.com can be used.
"""
from __future__ import annotations

import hashlib
import http.client
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from .errors import PtError
from .i18n import L

CHUNK = 1 << 20
ATTEMPTS = 3


def hf_endpoint() -> str:
    return os.environ.get("HF_ENDPOINT", "https://huggingface.co").rstrip("/")


def hf_url(repo: str, path: str) -> str:
    return f"{hf_endpoint()}/datasets/{repo}/resolve/main/{urllib.parse.quote(path)}"


class _Redirects(urllib.request.HTTPRedirectHandler):
    """urllib before Python 3.11 does not follow HTTP 308 (Permanent Redirect); Hugging Face mirrors use it. GET only."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):     # noqa: D401
        if code == 308:
            keep = {k: v for k, v in req.headers.items() if k.lower() not in ("content-length", "content-type")}
            return urllib.request.Request(newurl.replace(" ", "%20"), headers=keep, origin_req_host=req.origin_req_host,
                                          unverifiable=True)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

    http_error_308 = urllib.request.HTTPRedirectHandler.http_error_302


def _opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(_Redirects())


def open_url(url: str, lang: str, headers: dict[str, str] | None = None, timeout: int = 60):
    req = urllib.request.Request(url, headers={"User-Agent": "pathtrove-plugin", **(headers or {})})
    try:
        return _opener().open(req, timeout=timeout)
    except urllib.error.HTTPError as err:
        raise PtError(L(lang, f"HTTP {err.code} from {url}", f"{url} 返回 HTTP {err.code}")) from None
    except (urllib.error.URLError, OSError, http.client.HTTPException) as err:
        why = getattr(err, "reason", err)
        raise PtError(L(lang, f"cannot reach {url}: {why}", f"无法连接 {url}：{why}")) from None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest_dir: Path, name: str, size: int, sha256: str, lang: str, what: str = "") -> dict[str, Any]:
    """Download `url` to dest_dir/name and verify size and sha256. A partial `name.part` is resumed (Range) and an interrupted
    transfer is retried up to 3 times. On a mismatch the partial file is removed and PtError says so.
    Returns {path, size, sha256, url, already_present, resumed_from}."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    final, part = dest_dir / name, dest_dir / (name + ".part")
    if final.exists() and final.stat().st_size == size and sha256_file(final) == sha256:
        return {"path": final, "size": size, "sha256": sha256, "url": url, "already_present": True, "resumed_from": 0}
    resumed_from = None
    for attempt in range(1, ATTEMPTS + 1):
        last_err = ""
        h, have = hashlib.sha256(), 0
        if part.exists() and 0 < part.stat().st_size < size:              # resume an interrupted download
            with part.open("rb") as fh:
                for chunk in iter(lambda: fh.read(CHUNK), b""):
                    h.update(chunk)
                    have += len(chunk)
        else:
            part.unlink(missing_ok=True)
        if resumed_from is None:
            resumed_from = have
        resp = open_url(url, lang, {"Range": f"bytes={have}-"} if have else None, timeout=120)
        if have and getattr(resp, "status", 200) != 206:                    # server ignored Range: start over
            h, have = hashlib.sha256(), 0
            part.unlink(missing_ok=True)
        t_print = time.time()
        try:
            with part.open("ab" if have else "wb") as out:
                while chunk := resp.read(CHUNK):
                    out.write(chunk)
                    h.update(chunk)
                    have += len(chunk)
                    if size > (32 << 20) and time.time() - t_print > 10:
                        t_print = time.time()
                        print(f"{what or name}: {have / 1e6:.0f} / {size / 1e6:.0f} MB", file=sys.stderr, flush=True)
        except (OSError, http.client.HTTPException) as err:
            last_err = f"{type(err).__name__}: {err}"
        finally:
            resp.close()
        if have < size:
            last_err = last_err or L(lang, f"connection closed after {have} of {size} bytes", f"连接在 {have}/{size} 字节处关闭")
            if attempt < ATTEMPTS:
                continue
            raise PtError(L(lang,
                            f"download interrupted after {have} of {size} bytes ({last_err}) in {ATTEMPTS} attempts; the partial file "
                            f"{part} is kept, rerun the same call to resume",
                            f"下载在 {have}/{size} 字节处中断（{last_err}），已重试 {ATTEMPTS} 次；保留了未完成文件 {part}，重跑同一调用即可续传"))
        break
    if have != size or h.hexdigest() != sha256:
        part.unlink(missing_ok=True)
        raise PtError(L(lang,
                        f"verification failed for {name}: got {have} bytes, sha256 {h.hexdigest()}; expected {size} bytes, sha256 {sha256}. "
                        "The partial file was removed; nothing was installed. Retry, or use another HF_ENDPOINT.",
                        f"{name} 校验失败：收到 {have} 字节，sha256 {h.hexdigest()}；应为 {size} 字节，sha256 {sha256}。"
                        "已删除未完成文件，未安装任何内容。请重试，或换一个 HF_ENDPOINT。"))
    os.replace(part, final)
    return {"path": final, "size": have, "sha256": sha256, "url": url, "already_present": False, "resumed_from": resumed_from or 0}
