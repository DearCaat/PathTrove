"""Where the data package lives: a versioned archive on the public Hugging Face repo, unpacked into a user cache directory.

The plugin ships only `data-manifest.json` (data version, archive size and sha256, label file list). On first use the archive is
downloaded, verified against that sha256 and unpacked; `pathtrove data install --file` installs from a local copy instead.

  PATHTROVE_HOME     cache directory (default ~/.cache/pathtrove, or $XDG_CACHE_HOME/pathtrove; %LOCALAPPDATA%\\pathtrove on Windows)
  PATHTROVE_BUNDLE   use this already-unpacked directory as the data package (development)
  HF_ENDPOINT        Hugging Face host or mirror (default https://huggingface.co)
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tarfile
import time
from pathlib import Path
from typing import Any

from . import net
from .errors import PtError
from .i18n import L

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_FILE = PLUGIN_ROOT / "data-manifest.json"
MARKER = ".pathtrove-installed.json"
LOCK_STALE_SECONDS = 1800


def plugin_manifest() -> dict[str, Any]:
    if not MANIFEST_FILE.exists():
        raise PtError(f"plugin manifest missing: {MANIFEST_FILE}")
    return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))


def cache_root() -> Path:
    if os.environ.get("PATHTROVE_HOME"):
        return Path(os.environ["PATHTROVE_HOME"]).expanduser().resolve()
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "pathtrove"
    return Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "pathtrove"


def data_dir(manifest: dict[str, Any]) -> Path:
    return cache_root() / "data" / manifest["data_version"]


def archive_url(manifest: dict[str, Any]) -> str:
    return net.hf_url(manifest["hf_repo"], manifest["archive"]["path"])


def installed(manifest: dict[str, Any]) -> bool:
    marker = data_dir(manifest) / MARKER
    try:
        return json.loads(marker.read_text(encoding="utf-8")).get("archive_sha256") == manifest["archive"]["sha256"]
    except (OSError, ValueError):
        return False


def status(manifest: dict[str, Any]) -> dict[str, Any]:
    override = os.environ.get("PATHTROVE_BUNDLE")
    return {"data_version": manifest["data_version"], "installed": bool(override) or installed(manifest),
            "location": override or str(data_dir(manifest)), "cache_root": str(cache_root()),
            "archive": {"url": archive_url(manifest), "size": manifest["archive"]["size"], "sha256": manifest["archive"]["sha256"]},
            "hf_endpoint": net.hf_endpoint(), "bundle_override": override or None}


def missing_help(manifest: dict[str, Any], lang: str, why: str) -> str:
    a = manifest["archive"]
    url = archive_url(manifest)
    return L(lang,
             f"PathTrove data {manifest['data_version']} is not installed and could not be downloaded: {why}\n"
             f"Fix: (1) retry when the network is back; (2) behind a firewall set HF_ENDPOINT to a mirror, e.g. HF_ENDPOINT=https://hf-mirror.com; "
             f"(3) download {url} ({a['size'] / 1e6:.1f} MB, sha256 {a['sha256']}) on any machine and install it with "
             f"`pathtrove data install --file <path to {a['name']}>`. The data is cached in {cache_root()} (set PATHTROVE_HOME to change).",
             f"PathTrove 数据 {manifest['data_version']} 尚未安装，且下载失败：{why}\n"
             f"处理办法：(1) 网络恢复后重试；(2) 处在防火墙后时把 HF_ENDPOINT 设为镜像，如 HF_ENDPOINT=https://hf-mirror.com；"
             f"(3) 在任意机器下载 {url}（{a['size'] / 1e6:.1f} MB，sha256 {a['sha256']}），再用 "
             f"`pathtrove data install --file <{a['name']} 的路径>` 离线安装。数据缓存在 {cache_root()}（用 PATHTROVE_HOME 更改）。")


# ---------------------------------------------------------------- locking, extraction

class _Lock:
    """One installer at a time (several MCP servers can start together). A lock older than 30 minutes is stale."""

    def __init__(self, path: Path):
        self.path = path

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.time() + LOCK_STALE_SECONDS
        while True:
            try:
                os.close(os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > LOCK_STALE_SECONDS:
                        self.path.unlink(missing_ok=True)
                        continue
                except OSError:
                    continue
                if time.time() > deadline:
                    raise PtError(f"another PathTrove install holds {self.path}; remove it if no install is running") from None
                time.sleep(0.5)

    def __exit__(self, *exc):
        self.path.unlink(missing_ok=True)


def _extract(archive: Path, target: Path, manifest: dict[str, Any], lang: str) -> None:
    tmp = target.parent / f".{target.name}.tmp-{os.getpid()}"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    try:
        with tarfile.open(archive, "r:gz") as tar:
            for m in tar.getmembers():
                p = Path(m.name)
                if not (m.isfile() or m.isdir()) or p.is_absolute() or ".." in p.parts:
                    raise PtError(L(lang, f"unsafe entry in the archive: {m.name!r}", f"压缩包含不安全的条目：{m.name!r}"))
            if sys.version_info >= (3, 12):
                tar.extractall(tmp, filter="data")
            else:
                tar.extractall(tmp)
        (tmp / MARKER).write_text(json.dumps({"archive_sha256": manifest["archive"]["sha256"], "data_version": manifest["data_version"],
                                              "installed_at": time.strftime("%Y-%m-%dT%H:%M:%S")}) + "\n", encoding="utf-8")
        if target.exists():
            shutil.rmtree(target)
        os.replace(tmp, target)
    except tarfile.TarError as err:
        raise PtError(L(lang, f"the archive cannot be unpacked: {err}", f"压缩包无法解开：{err}")) from None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def install_file(path: str | Path, lang: str) -> dict[str, Any]:
    """Install the archive from a local file after checking its size and sha256 against the plugin manifest."""
    manifest = plugin_manifest()
    src = Path(path).expanduser()
    if not src.is_file():
        raise PtError(L(lang, f"no such file: {src}", f"没有这个文件：{src}"))
    a = manifest["archive"]
    got = net.sha256_file(src)
    if src.stat().st_size != a["size"] or got != a["sha256"]:
        raise PtError(L(lang,
                        f"{src} is not the PathTrove {manifest['data_version']} data archive: size {src.stat().st_size} (expected {a['size']}), "
                        f"sha256 {got} (expected {a['sha256']}). Nothing was installed.",
                        f"{src} 不是 PathTrove {manifest['data_version']} 的数据包：大小 {src.stat().st_size}（应为 {a['size']}），"
                        f"sha256 {got}（应为 {a['sha256']}）。未安装任何内容。"))
    with _Lock(cache_root() / ".install.lock"):
        _extract(src, data_dir(manifest), manifest, lang)
    return status(manifest)


def ensure_data(lang: str, download: bool = True) -> Path:
    """The directory of the unpacked data package; downloads and installs it on first use."""
    override = os.environ.get("PATHTROVE_BUNDLE")
    if override:
        p = Path(override).expanduser().resolve()
        if not (p / "table_snapshot.json").exists():
            raise PtError(L(lang, f"PATHTROVE_BUNDLE={p} is not an unpacked data package (no table_snapshot.json)",
                            f"PATHTROVE_BUNDLE={p} 不是已解压的数据包（缺少 table_snapshot.json）"))
        return p
    manifest = plugin_manifest()
    target = data_dir(manifest)
    if installed(manifest):
        return target
    if not download:
        raise PtError(missing_help(manifest, lang, L(lang, "not downloaded yet", "尚未下载")))
    a = manifest["archive"]
    print(f"PathTrove: downloading data {manifest['data_version']} ({a['size'] / 1e6:.1f} MB) from {net.hf_endpoint()} to {cache_root()} ...",
          file=sys.stderr, flush=True)
    try:
        with _Lock(cache_root() / ".install.lock"):
            if installed(manifest):                                    # another process finished while we waited
                return target
            got = net.download(archive_url(manifest), cache_root() / "download", a["name"], a["size"], a["sha256"], lang, "PathTrove data")
            _extract(got["path"], target, manifest, lang)
            got["path"].unlink(missing_ok=True)
    except PtError as err:
        raise PtError(missing_help(manifest, lang, str(err))) from None
    except OSError as err:
        raise PtError(missing_help(manifest, lang, f"{type(err).__name__}: {err}")) from None
    print("PathTrove: data installed.", file=sys.stderr, flush=True)
    return target
