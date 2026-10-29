"""T2.1 loopback-only reference web shell; NOT a hosted/authenticated service.

The HTTP layer is deliberately thin: every mutation is a validated T1 command
on a freshly loaded persistent engine. Never expose this development handler
on a public interface until the T3 authentication/authorization port exists.
"""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
from threading import Lock
from urllib.parse import urlsplit

from .errors import NotFound, TreeError
from .projections import project_outline
from .storage import PersistentCommandEngine, RevisionConflict
from .tree import NodeKind

WEB_ROOT = Path(__file__).resolve().parents[2] / "web"
MAX_COMMAND_BYTES = 16 * 1024
ACTOR = "prototype:unverified-local-operator"

def _strict_json_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def _reject_nonfinite(value: str):
    raise ValueError("Nonfinite JSON constant")


_STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.css": ("app.css", "text/css; charset=utf-8"),
    "/app.mjs": ("app.mjs", "text/javascript; charset=utf-8"),
    "/tree-model.mjs": ("tree-model.mjs", "text/javascript; charset=utf-8"),
}


class ShellService:
    """Request-scoped engine loads avoid silently reusing a stale writer."""

    def __init__(self, database: str | Path):
        self.database = str(database)
        self.lock = Lock()
        PersistentCommandEngine(self.database)

    def workspace(self) -> dict:
        with self.lock:
            engine = PersistentCommandEngine(self.database)
            projects = sorted(engine.projects(), key=lambda item: (item.name.casefold(), item.id))
            outlines = {}
            for project in projects:
                outline = project_outline(engine, project.id)
                parent_ids = {row.node.parent_id for row in outline}
                effective_archive: dict[str, bool] = {}
                rows = []
                for row in outline:
                    node = row.node
                    inherited = effective_archive.get(node.parent_id, False)
                    effective_archive[node.id] = node.archived or inherited
                    rows.append({
                        "id": node.id,
                        "project_id": node.project_id,
                        "parent_id": node.parent_id,
                        "position": node.position,
                        "depth": row.depth,
                        "has_children": node.id in parent_ids,
                        "title": node.title,
                        "kind": node.kind.value,
                        "archived": node.archived,
                        "effectively_archived": effective_archive[node.id],
                    })
                outlines[project.id] = rows
            return {
                "revision": engine.storage_revision,
                "projects": [{"id": p.id, "name": p.name} for p in projects],
                "outlines": outlines,
            }

    def execute(self, request: object) -> dict:
        if type(request) is not dict:
            raise TreeError("Command must be a JSON object")
        action = request.get("type")
        schemas = {
            "project.create": ({"type", "expected_revision", "name"}, set()),
            "node.create": (
                {"type", "expected_revision", "project_id", "title"},
                {"parent_id", "kind", "position"},
            ),
            "node.rename": (
                {"type", "expected_revision", "project_id", "node_id", "title"}, set(),
            ),
            "node.archive": (
                {"type", "expected_revision", "project_id", "node_id"}, set(),
            ),
            "node.restore": (
                {"type", "expected_revision", "project_id", "node_id"}, set(),
            ),
            "node.move": (
                {"type", "expected_revision", "project_id", "node_id", "new_parent_id"},
                {"position"},
            ),
        }
        if type(action) is not str or action not in schemas:
            raise TreeError("Unsupported command")
        required, optional = schemas[action]
        if not required.issubset(request) or set(request) - (required | optional):
            raise TreeError("Invalid command fields")
        revision = request["expected_revision"]
        if type(revision) is not int or revision < 0:
            raise TreeError("Invalid expected revision")
        with self.lock:
            engine = PersistentCommandEngine(self.database)
            if engine.storage_revision != revision:
                raise RevisionConflict("Workspace changed; reload before editing")
            kwargs = {"actor": ACTOR}
            if action == "project.create":
                result = engine.create_project(request["name"], **kwargs)
            else:
                project_id = request["project_id"]
                if type(project_id) is not str:
                    raise TreeError("Invalid project identity")
                if action == "node.create":
                    kind = request.get("kind", NodeKind.TASK.value)
                    if type(kind) is not str:
                        raise TreeError("Invalid node kind")
                    try:
                        kind = NodeKind(kind)
                    except ValueError as exc:
                        raise TreeError("Invalid node kind") from exc
                    result = engine.create_node(
                        project_id, request["title"],
                        parent_id=request.get("parent_id"),
                        position=request.get("position"), kind=kind, **kwargs,
                    )
                elif action == "node.rename":
                    result = engine.rename_node(
                        project_id, request["node_id"], request["title"], **kwargs,
                    )
                elif action == "node.archive":
                    result = engine.archive_node(project_id, request["node_id"], **kwargs)
                elif action == "node.restore":
                    result = engine.restore_node(project_id, request["node_id"], **kwargs)
                else:
                    result = engine.move_node(
                        project_id, request["node_id"],
                        new_parent_id=request["new_parent_id"],
                        position=request.get("position"), **kwargs,
                    )
            return {"id": result.id, "revision": engine.storage_revision}


class TreeShellHandler(BaseHTTPRequestHandler):
    """Hardcoded route whitelist, strict loopback Host and write Origin checks."""

    server_version = "ARTPrototype/0.1"

    def _allowed_origins(self) -> set[str]:
        port = self.server.server_address[1]
        return {f"http://127.0.0.1:{port}", f"http://localhost:{port}"}

    def _valid_host(self) -> bool:
        return self.headers.get("Host") in {
            origin.removeprefix("http://") for origin in self._allowed_origins()
        }

    def _respond(self, status: int, payload: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; base-uri 'none'; frame-ancestors 'none'",
        )
        self.end_headers()
        self.wfile.write(payload)

    def _json(self, status: int, data: dict) -> None:
        self._respond(
            status, json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
            "application/json; charset=utf-8",
        )

    def _error(self, status: int, reason: str) -> None:
        self._json(status, {"error": reason})

    def do_GET(self) -> None:
        if not self._valid_host():
            self._error(400, "Invalid host")
            return
        try:
            path = urlsplit(self.path)
        except ValueError:
            self._error(404, "Not found")
            return
        if path.query or path.fragment:
            self._error(404, "Not found")
            return
        if path.path == "/api/workspace":
            try:
                self._json(200, self.server.service.workspace())
            except (TreeError, sqlite3.DatabaseError):
                self._error(503, "Storage unavailable or invalid")
            return
        static = _STATIC.get(path.path)
        if static is None:
            self._error(404, "Not found")
            return
        name, media_type = static
        try:
            content = (WEB_ROOT / name).read_bytes()
        except OSError:
            self._error(503, "Web asset unavailable")
            return
        self._respond(200, content, media_type)

    def do_POST(self) -> None:
        if not self._valid_host():
            self._error(400, "Invalid host")
            return
        if self.path != "/api/commands":
            self._error(404, "Not found")
            return
        if (self.headers.get("Origin") not in self._allowed_origins()
                or self.headers.get("Sec-Fetch-Site", "same-origin") not in
                ("same-origin", "none")):
            self._error(403, "Cross-origin writes are forbidden")
            return
        if self.headers.get("Content-Type") != "application/json":
            self._error(415, "Expected application/json")
            return
        lengths = self.headers.get_all("Content-Length") or []
        if self.headers.get("Transfer-Encoding") is not None or len(lengths) != 1:
            self._error(400, "Invalid request length")
            return
        try:
            length = int(lengths[0])
            if not 0 < length <= MAX_COMMAND_BYTES:
                self._error(413, "Command too large or empty")
                return
            payload = self.rfile.read(length)
            request = json.loads(
                payload.decode("utf-8"), object_pairs_hook=_strict_json_pairs,
                parse_constant=_reject_nonfinite,
            )
            result = self.server.service.execute(request)
        except RevisionConflict:
            self._error(409, "Workspace changed; reload before editing")
        except NotFound:
            self._error(404, "Project or node not found")
        except TreeError as exc:
            self._error(422, str(exc))
        except (ValueError, UnicodeError, json.JSONDecodeError):
            self._error(400, "Invalid JSON command")
        except sqlite3.DatabaseError:
            self._error(503, "Storage unavailable or invalid")
        else:
            self._json(200, result)

    def do_PUT(self) -> None:
        self._error(405, "Method not allowed")

    def do_DELETE(self) -> None:
        self._error(405, "Method not allowed")

    def log_message(self, fmt: str, *args: object) -> None:
        # No URL/body/identity-bearing development request logs.
        return


def make_server(database: str | Path, port: int = 8765, host: str = "127.0.0.1"):
    if host != "127.0.0.1":
        raise ValueError("T2.1 has no authentication: loopback is mandatory")
    service = ShellService(database)
    server = ThreadingHTTPServer((host, port), TreeShellHandler)
    server.daemon_threads = True
    server.service = service
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="T2.1 local-only tree web prototype")
    parser.add_argument("--db", type=Path, default=Path(".local/tree-shell.db"))
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--demo", action="store_true", help="Seed synthetic demo nodes once")
    args = parser.parse_args()
    args.db.parent.mkdir(parents=True, exist_ok=True)
    if args.demo:
        engine = PersistentCommandEngine(args.db)
        if not engine.projects():
            project = engine.create_project("Synthetic roadmap", actor=ACTOR)
            foundation = engine.create_node(
                project.id, "Foundation", kind=NodeKind.MILESTONE, actor=ACTOR,
            )
            engine.create_node(
                project.id, "Canonical model", parent_id=foundation.id,
                kind=NodeKind.SUBMILESTONE, actor=ACTOR,
            )
            engine.create_node(
                project.id, "Tree-first workspace", kind=NodeKind.MILESTONE, actor=ACTOR,
            )
    server = make_server(args.db, args.port)
    print(f"T2.1 local prototype: http://127.0.0.1:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
