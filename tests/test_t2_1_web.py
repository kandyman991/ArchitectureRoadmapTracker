"""T2.1 synthetic end-to-end HTTP/security tests, without browser automation."""
from __future__ import annotations

import http.client
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest

from architecture_roadmap_tracker import PersistentCommandEngine
from architecture_roadmap_tracker.web import make_server


class WebShellHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / "reference.db"
        self.server = make_server(self.database, port=0)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    @property
    def host(self):
        return "127.0.0.1:" + str(self.server.server_address[1])

    def request(self, method, path, body=None, *, origin=True, host=None, content_type="application/json"):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_address[1], timeout=5)
        headers = {"Host": self.host if host is None else host}
        if method == "POST":
            if origin is True:
                headers["Origin"] = "http://" + self.host
            elif isinstance(origin, str):
                headers["Origin"] = origin
            headers["Content-Type"] = content_type
            body = json.dumps(body) if isinstance(body, dict) else body
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        raw = response.read()
        status = response.status
        response_headers = dict(response.getheaders())
        connection.close()
        if response_headers.get("Content-Type", "").startswith("application/json"):
            return status, json.loads(raw), response_headers
        return status, raw.decode(), response_headers

    def workspace(self):
        status, body, _ = self.request("GET", "/api/workspace")
        self.assertEqual(status, 200)
        return body

    def command(self, action, revision=None, **fields):
        if revision is None:
            revision = self.workspace()["revision"]
        return self.request("POST", "/api/commands", {
            "type": action, "expected_revision": revision, **fields,
        })[:2]

    def test_empty_shell_and_same_origin_static_assets(self):
        self.assertEqual(self.workspace()["projects"], [])
        self.assertEqual(self.workspace()["outlines"], {})
        for path, fragment in [
            ("/", "Roadmap tree"),
            ("/app.css", ".tree-row"),
            ("/app.mjs", "textContent"),
            ("/tree-model.mjs", "visibleOutline"),
        ]:
            status, body, headers = self.request("GET", path)
            self.assertEqual(status, 200)
            self.assertIn(fragment, body)
            self.assertIn("default-src 'none'", headers["Content-Security-Policy"])
            self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(self.request("GET", "/../ARCHITECTURE.md")[0], 404)
        self.assertEqual(self.request("GET", "/api/workspace?secret=1")[0], 404)
        self.assertEqual(self.request("GET", "/api/workspace", host="evil.example")[0], 400)
        with self.assertRaises(ValueError):
            make_server(self.database, host="0.0.0.0", port=0)

    def test_commands_use_canonical_engine_and_survive_restart(self):
        status, project = self.command("project.create", name="Synthetic plan")
        self.assertEqual(status, 200)
        pid = project["id"]
        status, first = self.command("node.create", project_id=pid, title="First", kind="milestone")
        self.assertEqual(status, 200)
        status, second = self.command(
            "node.create", project_id=pid, parent_id=first["id"],
            title="Second", kind="submilestone",
        )
        self.assertEqual(status, 200)
        status, third = self.command("node.create", project_id=pid, title="Third")
        self.assertEqual(status, 200)
        view = self.workspace()
        self.assertEqual([n["title"] for n in view["outlines"][pid]], ["First", "Second", "Third"])
        self.assertEqual([n["depth"] for n in view["outlines"][pid]], [0, 1, 0])
        self.assertTrue(view["outlines"][pid][0]["has_children"])
        self.assertEqual([n["position"] for n in view["outlines"][pid]], [0, 0, 1])
        self.assertEqual(view["revision"], 4)

        status, _ = self.command(
            "node.move", project_id=pid, node_id=third["id"],
            new_parent_id=None, position=0,
        )
        self.assertEqual(status, 200)
        self.assertEqual(
            [n["title"] for n in self.workspace()["outlines"][pid]],
            ["Third", "First", "Second"],
        )
        status, _ = self.command("node.archive", project_id=pid, node_id=first["id"])
        self.assertEqual(status, 200)
        status, _ = self.command(
            "node.rename", project_id=pid, node_id=second["id"], title="Forbidden",
        )
        self.assertEqual(status, 422)
        status, _ = self.command("node.restore", project_id=pid, node_id=first["id"])
        self.assertEqual(status, 200)
        status, _ = self.command(
            "node.rename", project_id=pid, node_id=second["id"], title="Renamed",
        )
        self.assertEqual(status, 200)

        reopened = PersistentCommandEngine(self.database)
        self.assertEqual(reopened.node(pid, second["id"]).title, "Renamed")
        self.assertEqual(len(reopened.audit_log(pid)), 8)
        self.assertEqual(reopened.storage_revision, 8)

    def test_rejects_stale_writes_cross_project_scope_and_extra_fields(self):
        _, a = self.command("project.create", name="A")
        _, b = self.command("project.create", name="B")
        _, node = self.command("node.create", project_id=a["id"], title="Confidential synthetic node")
        original_revision = self.workspace()["revision"]
        status, response = self.command(
            "node.rename", revision=original_revision, project_id=b["id"],
            node_id=node["id"], title="Wrong tenant",
        )
        self.assertEqual(status, 404)
        self.assertIn("not found", response["error"])
        status, response = self.request("POST", "/api/commands", {
            "type": "node.rename", "expected_revision": original_revision,
            "project_id": a["id"], "node_id": node["id"],
            "title": "Forged actor", "actor": "admin",
        })[:2]
        self.assertEqual(status, 422)
        self.assertIn("fields", response["error"])
        _, project = self.command("project.create", name="New revision")
        self.assertNotEqual(project["revision"], original_revision)
        status, response = self.command(
            "node.rename", revision=original_revision,
            project_id=a["id"], node_id=node["id"], title="Stale",
        )
        self.assertEqual(status, 409)
        self.assertEqual(PersistentCommandEngine(self.database).node(a["id"], node["id"]).title,
                         "Confidential synthetic node")
        self.assertEqual(len(PersistentCommandEngine(self.database).audit_log(a["id"])), 2)

    def test_rejects_csrf_hostile_requests_and_invalid_commands(self):
        original = self.workspace()
        payload = {"type": "project.create", "expected_revision": 0, "name": "Injected"}
        self.assertEqual(self.request("POST", "/api/commands", payload, origin=False)[0], 403)
        self.assertEqual(self.request("POST", "/api/commands", payload,
                                      origin="https://example.org")[0], 403)
        self.assertEqual(self.request("POST", "/api/commands", payload,
                                      host="attacker.example")[0], 400)
        self.assertEqual(self.request("POST", "/api/commands", payload,
                                      content_type="text/plain")[0], 415)
        self.assertEqual(self.request("POST", "/api/commands", "not-json")[0], 400)
        self.assertEqual(self.request("POST", "/api/commands", {
            "type": "arbitrary.approve", "expected_revision": 0,
        })[0], 422)
        self.assertEqual(self.request("POST", "/api/commands", payload,
                                      origin=True)[0], 200)
        self.assertEqual(self.workspace()["revision"], original["revision"] + 1)
        self.assertEqual(self.request("DELETE", "/api/commands")[0], 405)


if __name__ == "__main__":
    unittest.main()
