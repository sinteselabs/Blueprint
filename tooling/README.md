# tooling/

Tooling that is **installed once per machine**, not copied into projects. When you
create a project from Blueprint, leave this folder out (see the copy step in the
root `README.md`). Everything here is optional: each tool is one way to do a job,
and any tool that does the same job can replace it.

| Tool | Job |
|---|---|
| [`claude-code/langfuse_hook.py`](claude-code/langfuse_hook.py) | Sends every Claude Code session to [Langfuse](https://langfuse.com): one trace per turn, with the model, token usage and each tool call |
| [`checks/`](checks/) | Checks for the Blueprint repository itself: internal links, the hook, the root, the skills and shared text (see [below](#checks-for-this-repository)) |

---

## Langfuse hook for Claude Code

Set it up once and forget it. From then on, every turn of every Claude Code session
in a configured repository is recorded, and you open Langfuse only when you need to
look something up.

### What it sends

For each turn of a Claude Code session: a trace named `Claude Code - Turn N`,
carrying the Claude Code session id and the user (`CC_LANGFUSE_USER_ID`, or the OS
user name). It is tagged `claude-code`, `lore:<workspace>/<project>` (read from the
nearest `.ai-memory.toml` above the session's folder, when there is one) and
`branch:<git branch>` (worktrees included); the same values go in the trace
metadata. Under it, one generation per assistant message (model, input and output
tokens, cache tokens) and one span per tool call with its input and output. Text is
cut at 20,000 characters per field (`CC_LANGFUSE_MAX_CHARS`).

It does **not** mask anything. Prompts, outputs and tool results go as they are,
including a secret pasted into the chat. Keep out of agent sessions whatever must
not reach your Langfuse project.

It **fails open**: whatever goes wrong, it exits 0 and never blocks the session.
It does not fail silently, though. When it is switched on and cannot record (SDK
missing, keys missing, Langfuse refusing the data), it says so in the session, in
one line, and writes the reason to `~/.claude/state/langfuse_hook.log`. When it is
switched off (`TRACE_TO_LANGFUSE` is not `true`), it only logs. That is what lets
you forget it: silence means it is recording.

What it does not cover: sessions that run where the hook is not installed, such as
cloud sessions. How much of a subagent's inner work reaches the trace has not been
measured.

### How it joins with lore

lore's capture hooks record the same Claude Code session id on each session page,
and the `lore:` tag carries the same workspace and project that lore uses. So a
trace can be found from a lore session page and the other way round, and Langfuse
can be filtered by lore project even when several repositories share one Langfuse
project.

### Setup, once per machine

1. **Install the SDK** in the Python that will run the hook: `pip install "langfuse>=4,<5"`.
   The hook relies on internals of SDK 4.x and says so in its log if they change.
2. **Copy the script** to `~/.claude/hooks/langfuse_hook.py`
   (on Windows, `C:\Users\<you>\.claude\hooks\langfuse_hook.py`).
3. **Register it** in the user-level `~/.claude/settings.json`:

   ```json
   {
     "hooks": {
       "Stop": [
         { "hooks": [ { "type": "command", "command": "python3 ~/.claude/hooks/langfuse_hook.py" } ] }
       ]
     }
   }
   ```

   On Windows, name the Python that has the SDK, for example
   `py -3.13 C:/Users/<you>/.claude/hooks/langfuse_hook.py`. A second Python on the
   machine without the SDK is the usual cause of "cannot import the Langfuse SDK".
4. **Set the variables**, in the `env` block of a Claude Code settings file:
   - one Langfuse project for everything on this machine: `~/.claude/settings.json`;
   - one Langfuse project per repository: that repository's
     `.claude/settings.local.json`, which must be git-ignored. Use the `CC_` names
     there.

   ```json
   {
     "env": {
       "TRACE_TO_LANGFUSE": "true",
       "CC_LANGFUSE_PUBLIC_KEY": "pk-lf-...",
       "CC_LANGFUSE_SECRET_KEY": "sk-lf-...",
       "CC_LANGFUSE_BASE_URL": "https://cloud.langfuse.com"
     }
   }
   ```

   | Variable | Needed | Meaning |
   |---|---|---|
   | `TRACE_TO_LANGFUSE` | **yes**, `true` | Without it the hook does nothing |
   | `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` | **yes** | The Langfuse project's key pair. The `CC_LANGFUSE_*` versions take precedence, so Claude Code can be traced into a different project than an application's own keys |
   | `LANGFUSE_BASE_URL` | **yes, unless EU cloud** | The host of your Langfuse project: `https://cloud.langfuse.com` (EU, the default), `https://us.cloud.langfuse.com` (US), or your own. `CC_LANGFUSE_BASE_URL` takes precedence; `LANGFUSE_HOST` is accepted as a fallback. A project lives on one host, so check which one yours is on |
   | `CC_LANGFUSE_USER_ID` | no | Who the traces belong to. Default: the OS user name |
   | `CC_LANGFUSE_DEBUG` | no | `true` writes detail to the log |
   | `CC_LANGFUSE_MAX_CHARS` | no | Cut-off per text field, default 20000 |

   Claude Code reads `.claude/settings.local.json` only in the folder a session
   starts in. A git worktree of the repository, or a subfolder, does not get it, so
   the hook looks for that file itself (in the folder, up to the repository root,
   and in the main checkout a worktree belongs to) whenever the environment says
   nothing about `TRACE_TO_LANGFUSE`. To switch tracing off for one session, set
   `TRACE_TO_LANGFUSE=false` in the environment.

   Never commit keys.
5. **Check it works.** Run a short session, then open the Langfuse project: a trace
   `Claude Code - Turn 1` with tokens and cost must be there, **and it must carry the
   `branch:` tag** (and the `lore:` tag, in a repository with `.ai-memory.toml`). A
   trace that arrives without them means the hook could not read the session's
   folder. If nothing arrives, read `~/.claude/state/langfuse_hook.log`.

State and logs live in `~/.claude/state/` (`langfuse_state.json` remembers how far
each transcript was read, so a turn is never sent twice).

---

## Checks for this repository

Scripts that must pass before a change to Blueprint is integrated. They check
Blueprint itself, not the projects made from it.

| Check | What it guards | Run |
|---|---|---|
| [`checks/check_links.py`](checks/check_links.py) | No internal Markdown link points at a file that does not exist | `python tooling/checks/check_links.py` |
| [`checks/test_langfuse_hook.py`](checks/test_langfuse_hook.py) | The hook sends a turn once, tagged, from a folder with an accent in its path; stays quiet when switched off; tells the person when switched on and broken | `python tooling/checks/test_langfuse_hook.py` |
| [`checks/check_root_names.py`](checks/check_root_names.py) | Nothing at the root has a name the plugin loads on its own (`.mcp.json`, `hooks/`, `bin/` and the like). The root is the plugin root | `python tooling/checks/check_root_names.py` |
| [`checks/check_skills.py`](checks/check_skills.py) | Every skill follows the format: a name equal to its folder, a description within the limit, `SKILL.md` within 500 lines, no link out of its own folder | `python tooling/checks/check_skills.py` |
| [`checks/check_shared_text.py`](checks/check_shared_text.py) | Copies of a text shared between skills are identical | `python tooling/checks/check_shared_text.py` |
| [`checks/check_state.py`](checks/check_state.py) | The project state example and template that the record skill ships follow the state format. Given a file, it checks that file instead | `python tooling/checks/check_state.py` |
| [`checks/test_checks.py`](checks/test_checks.py) | The four checks above pass on a sound input and fail on a planted error | `python tooling/checks/test_checks.py` |

A skill can only point at files inside its own folder, so a text that several
skills need is copied into each of them. Mark each copy, and
`check_shared_text.py` keeps them identical:

```
<!-- shared: NAME -->
the text
<!-- /shared: NAME -->
```

The structure checks need only Python. The first three take an optional folder
to check instead of this repository, and `check_state.py` takes state files,
which is how `test_checks.py` plants its errors.

`check_state.py` reads the format described in
[`skills/blueprint-record/references/state-format.md`](../skills/blueprint-record/references/state-format.md).
It is this repository's own tooling: the check that Blueprint runs in a project
is a separate script, shipped with the skills.

The hook test needs the Langfuse SDK and nothing else: it runs against an HTTP
server it starts itself, with a throwaway home folder, so it needs no account and
leaves your own state and log alone.
