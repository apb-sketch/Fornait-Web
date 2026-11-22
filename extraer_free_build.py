"""Repite la extracción de los recursos de Free Build incluidos en el inventario."""

import argparse
from collections import Counter
from itertools import count
import json
import os
from pathlib import Path, PurePosixPath
import shutil
from tempfile import NamedTemporaryFile
from urllib.request import Request, urlopen


class FortnitePorting:
    def __init__(self, url):
        self.url = url
        self.headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
        self.ids = count(1)
        result = self.rpc("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "free-build-export", "version": "1.0"},
        })
        self.headers["MCP-Protocol-Version"] = result["protocolVersion"]
        self.rpc("notifications/initialized", notification=True)

    def rpc(self, method, params=None, *, notification=False):
        request = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            request["params"] = params
        if not notification:
            request["id"] = next(self.ids)
        body = json.dumps(request).encode("utf-8")
        with urlopen(Request(self.url, data=body, headers=self.headers), timeout=60) as response:
            if notification:
                return None
            if response.headers.get_content_type() == "text/event-stream":
                events = (line[6:] for line in response if line.startswith(b"data: "))
                packet = next(json.loads(event) for event in events)
            else:
                packet = json.load(response)
        if "error" in packet:
            raise RuntimeError(packet["error"])
        return packet["result"]

    def call(self, name, arguments):
        result = self.rpc("tools/call", {"name": name, "arguments": arguments})
        payload = json.loads(result["content"][0]["text"])
        if result.get("isError") or payload.get("error"):
            raise RuntimeError(payload.get("error", name))
        return payload


def relative_path(value):
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part == ".." or ":" in part or "\\" in part for part in path.parts):
        raise ValueError(f"Ruta fuera del inventario: {value}")
    return Path(*path.parts)


def valid_file(path):
    if not path.is_file() or not path.stat().st_size:
        return False
    signatures = {
        ".ueanim": b"UEFORMAT", ".uemodel": b"UEFORMAT", ".uepose": b"UEFORMAT",
        ".png": b"\x89PNG\r\n\x1a\n", ".wav": b"RIFF",
    }
    signature = signatures.get(path.suffix.lower())
    if signature is None:
        return True
    with path.open("rb") as stream:
        return stream.read(len(signature)) == signature


def copy_verified(source, destination):
    if destination.exists() and source.read_bytes() == destination.read_bytes():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=destination.parent, delete=False) as file:
        pending = Path(file.name)
    try:
        shutil.copy2(source, pending)
        pending.replace(destination)
    finally:
        pending.unlink(missing_ok=True)
    return True


def main():
    project = Path(__file__).resolve().parent
    library = project / "recursos" / "Free_Build_Fortnite"
    default_cache = Path(os.environ.get("LOCALAPPDATA", str(project))) / "FortnitePorting" / "Assets"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventario", type=Path, default=library / "06_Referencias" / "Inventario_43.10.json")
    parser.add_argument("--destino", type=Path, default=library)
    parser.add_argument("--origen", type=Path, default=default_cache, help="Carpeta Assets de Fortnite Porting")
    parser.add_argument("--url", default="http://127.0.0.1:6010/mcp")
    parser.add_argument("--solo-organizar", action="store_true", help="Usa la caché existente sin llamar al MCP")
    args = parser.parse_args()

    with args.inventario.open(encoding="utf-8") as file:
        rows = json.load(file)["archivos"]
    origin = args.origen
    client = None
    tried = {}
    missing = []
    counts = Counter()
    for row in rows:
        destination = args.destino / relative_path(row["destino"])
        local = relative_path(row["origen"])
        source = (origin if row["base"] == "Assets" else project) / local
        try:
            if not valid_file(source) and valid_file(destination):
                counts["ya presentes"] += 1
                continue
            if not valid_file(source) and row.get("unreal") and not args.solo_organizar:
                if client is None:
                    client = FortnitePorting(args.url)
                    status = client.call("fortnite_status", {})
                    if not status["fortnite"]["ready"]:
                        raise RuntimeError("Fortnite Porting todavía está cargando los datos")
                    origin = Path(status["exportTargets"]["assetsFolder"]["path"])
                    source = origin / local
                asset = row["unreal"]
                if not valid_file(source) and asset not in tried:
                    try:
                        client.call("fortnite_export_asset", {"path": asset, "target": "assets_folder"})
                    except (OSError, RuntimeError, ValueError, KeyError) as exc:
                        tried[asset] = str(exc)
                    else:
                        tried[asset] = None
            if valid_file(source):
                counts["copiados" if copy_verified(source, destination) else "ya presentes"] += 1
            else:
                missing.append((row["destino"], tried.get(row.get("unreal")) or "El exportador no produjo el archivo"))
        except (OSError, RuntimeError, ValueError, KeyError) as exc:
            missing.append((row["destino"], str(exc)))

    print(f"{counts['copiados']} copiados, {counts['ya presentes']} ya presentes, {len(missing)} pendientes")
    print(args.destino.resolve())
    for path, reason in missing:
        print(f"{path}: {reason}")
    return int(bool(missing))


if __name__ == "__main__":
    raise SystemExit(main())
