#!/usr/bin/env python3
"""
Offline test of tooling/claude-code/langfuse_hook.py.

Needs no Langfuse account and touches nothing in your home folder: the hook runs
against an HTTP server started here, with a throwaway home. Run it with the Python
that has the Langfuse SDK:

    python tooling/checks/test_langfuse_hook.py

Exit code 0 when every case passes, 1 otherwise, 2 when the SDK is missing.
"""

import gzip
import json
import os
import subprocess
import sys
import tempfile
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "claude-code" / "langfuse_hook.py"

try:
    import langfuse
except Exception as e:  # the hook would skip for the same reason
    print(f'cannot import the Langfuse SDK ({type(e).__name__}: {e}); run: pip install "langfuse>=4,<5"')
    sys.exit(2)
SDK_PATH = str(Path(langfuse.__file__).resolve().parents[1])


class Endpoint:
    """A local stand-in for Langfuse: records what it receives, answers `status`."""

    def __init__(self, status: int = 200) -> None:
        self.status = status
        self.posts = []  # (path, body)
        endpoint = self

        class Handler(BaseHTTPRequestHandler):
            def _answer(self) -> None:
                body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
                if self.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
                if self.command == "POST":
                    endpoint.posts.append((self.path, body))
                self.send_response(endpoint.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", "2")
                self.end_headers()
                self.wfile.write(b"{}")

            do_GET = do_POST = _answer

            def log_message(self, *args) -> None:
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def traces(self):
        return [body for path, body in self.posts if path.endswith("/v1/traces")]

    def close(self) -> None:
        self.server.shutdown()


def make_project(root: Path) -> Path:
    """A folder with a non-ASCII name, a lore marker and a git branch."""
    project = root / "projeto-açaí"
    (project / ".git").mkdir(parents=True)
    (project / ".git" / "HEAD").write_text("ref: refs/heads/feat/demo\n", encoding="utf-8")
    (project / ".ai-memory.toml").write_text('workspace = "demo"\nproject   = "Demo"\n', encoding="utf-8")
    return project


def make_worktree(root: Path, endpoint_url: str) -> Path:
    """A main checkout whose settings switch tracing on, and a git worktree of it."""
    main = root / "main-checkout"
    (main / ".git" / "worktrees" / "wt").mkdir(parents=True)
    (main / ".git" / "worktrees" / "wt" / "HEAD").write_text("ref: refs/heads/feat/wt\n", encoding="utf-8")
    (main / ".claude").mkdir()
    (main / ".claude" / "settings.local.json").write_text(json.dumps({"env": {
        "TRACE_TO_LANGFUSE": "true", "CC_LANGFUSE_PUBLIC_KEY": "pk-lf-test",
        "CC_LANGFUSE_SECRET_KEY": "sk-lf-test", "CC_LANGFUSE_BASE_URL": endpoint_url}}), encoding="utf-8")
    worktree = main / ".worktrees" / "wt"
    worktree.mkdir(parents=True)
    (worktree / ".git").write_text(f"gitdir: {main / '.git' / 'worktrees' / 'wt'}\n", encoding="utf-8")
    return worktree


def make_transcript(root: Path, session_id: str) -> Path:
    now = datetime.now(timezone.utc)
    stamp = lambda d: d.isoformat().replace("+00:00", "Z")
    rows = [
        {"type": "user", "timestamp": stamp(now - timedelta(seconds=4)),
         "message": {"role": "user", "content": "Synthetic turn."}},
        {"type": "assistant", "timestamp": stamp(now - timedelta(seconds=1)),
         "message": {"id": "msg_1", "role": "assistant", "model": "claude-test",
                     "content": [{"type": "text", "text": "Synthetic reply."}],
                     "usage": {"input_tokens": 12, "output_tokens": 4}}},
    ]
    path = root / f"{session_id}.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return path


def run_hook(home: Path, project: Path, transcript: Path, session_id: str, **variables: str):
    """Runs the hook the way Claude Code does: a UTF-8 JSON payload on stdin."""
    payload = json.dumps(
        {"session_id": session_id, "transcript_path": str(transcript), "cwd": str(project), "hook_event_name": "Stop"},
        ensure_ascii=False,
    ).encode("utf-8")
    env = {k: v for k, v in os.environ.items() if "LANGFUSE" not in k.upper()}
    env.update({"HOME": str(home), "USERPROFILE": str(home), "PYTHONPATH": SDK_PATH, **variables})
    result = subprocess.run([sys.executable, str(HOOK)], input=payload, capture_output=True, env=env, timeout=120)
    log_file = home / ".claude" / "state" / "langfuse_hook.log"
    log = log_file.read_text(encoding="utf-8", errors="replace") if log_file.exists() else ""
    return result.returncode, result.stdout.decode("utf-8", errors="replace").strip(), log


def main() -> int:
    failures = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        print(("PASS  " if ok else "FAIL  ") + name + (f"  [{detail}]" if detail and not ok else ""))
        if not ok:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        project = make_project(root)
        keys = {"LANGFUSE_PUBLIC_KEY": "pk-lf-test", "LANGFUSE_SECRET_KEY": "sk-lf-test"}

        # 1. A turn is sent, tagged with the lore project and the branch, from a path with an accent.
        home, endpoint = root / "home1", Endpoint()
        transcript = make_transcript(root, "session-1")
        code, out, log = run_hook(home, project, transcript, "session-1",
                                  TRACE_TO_LANGFUSE="true", LANGFUSE_BASE_URL=endpoint.url, **keys)
        sent = b"".join(endpoint.traces())
        check("exits 0", code == 0, f"exit {code}")
        check("sends the turn", len(endpoint.traces()) >= 1, f"{len(endpoint.posts)} requests, log: {log[-200:]}")
        check("tags the lore project", b"lore:demo/Demo" in sent)
        check("tags the branch", b"branch:feat/demo" in sent)
        check("says nothing to the person when all is well", out == "", out[:200])

        # 2. The same transcript is not sent twice.
        before = len(endpoint.traces())
        run_hook(home, project, transcript, "session-1",
                 TRACE_TO_LANGFUSE="true", LANGFUSE_BASE_URL=endpoint.url, **keys)
        check("does not send a turn twice", len(endpoint.traces()) == before, f"{len(endpoint.traces()) - before} more")
        endpoint.close()

        # 3. Switched off: nothing is sent, the log says why, the person is not bothered.
        home, endpoint = root / "home2", Endpoint()
        code, out, log = run_hook(home, project, make_transcript(root, "session-2"), "session-2",
                                  LANGFUSE_BASE_URL=endpoint.url, **keys)
        check("off without TRACE_TO_LANGFUSE: sends nothing", code == 0 and not endpoint.posts)
        check("off without TRACE_TO_LANGFUSE: logs the reason", "TRACE_TO_LANGFUSE" in log, log[-200:])
        check("off without TRACE_TO_LANGFUSE: stays quiet", out == "", out[:200])

        # 4. Switched on but broken: the person is told in the session.
        code, out, log = run_hook(home, project, make_transcript(root, "session-3"), "session-3",
                                  TRACE_TO_LANGFUSE="true", LANGFUSE_BASE_URL=endpoint.url)
        check("keys missing: sends nothing", code == 0 and not endpoint.posts)
        check("keys missing: tells the person", "systemMessage" in out and "KEY" in out, out[:200])
        endpoint.close()

        # 5. Langfuse refuses the data (wrong key or host): the person is told.
        home, endpoint = root / "home3", Endpoint(status=401)
        code, out, log = run_hook(home, project, make_transcript(root, "session-4"), "session-4",
                                  TRACE_TO_LANGFUSE="true", LANGFUSE_BASE_URL=endpoint.url, **keys)
        check("refused by Langfuse: exits 0", code == 0, f"exit {code}")
        check("refused by Langfuse: tells the person", "systemMessage" in out, f"stdout: {out[:200]} | log: {log[-300:]}")
        endpoint.close()

        # 6. A session in a git worktree has no settings file of its own: the main checkout's apply.
        home, endpoint = root / "home4", Endpoint()
        worktree = make_worktree(root, endpoint.url)
        code, out, log = run_hook(home, worktree, make_transcript(root, "session-5"), "session-5")
        sent = b"".join(endpoint.traces())
        check("in a worktree: sends the turn with the main checkout's settings", len(endpoint.traces()) >= 1, log[-300:])
        check("in a worktree: tags the worktree's branch", b"branch:feat/wt" in sent)

        # 7. The environment still decides: switched off there, the settings file does not switch it on.
        before = len(endpoint.posts)
        code, out, log = run_hook(home, worktree, make_transcript(root, "session-6"), "session-6",
                                  TRACE_TO_LANGFUSE="false")
        check("switched off in the environment: sends nothing", len(endpoint.posts) == before and out == "", out[:200])
        endpoint.close()

    print(f"\n{'OK' if not failures else 'FAILED'}: {len(failures)} failing check(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
