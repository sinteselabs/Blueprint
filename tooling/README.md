# tooling/

Tooling that is **installed once per machine**, not copied into projects. When you
create a project from Blueprint, leave this folder out (see the copy step in the
root `README.md`). Everything here is optional: each tool is one way to do a job,
and any tool that does the same job can replace it.

| Tool | Job |
|---|---|
| [`claude-code/langfuse_hook.py`](claude-code/langfuse_hook.py) | Sends every Claude Code session to [Langfuse](https://langfuse.com): one trace per turn, with the model, token usage and each tool call |
| [`checks/`](checks/) | Checks for the Blueprint repository itself: internal links, the hook, the root, the skills, shared text and the state format (see [below](#checks-for-this-repository)) |
| [`sessions/`](sessions/) | Tests that run a skill in real Claude Code sessions and check what was left on disk (see [below](#session-tests)) |

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

---

## Session tests

A skill is text that an agent follows, so the only real test of it is a session.
These tests run a skill in real Claude Code sessions, in a throwaway folder, and
then check the files the sessions left.

| Test | What it shows | Run |
|---|---|---|
| [`sessions/test_record_skill.py`](sessions/test_record_skill.py) | The record skill creates a state that passes `check_state.py`, updates it in a second session, records a decision and a session record each time, keeps a pasted key out of every file, and writes nothing outside the project | `python tooling/sessions/test_record_skill.py` |
| [`sessions/test_entry_skill.py`](sessions/test_entry_skill.py) | The blueprint skill finds the starting point in five situations (an empty folder, a folder with a state, a folder with code, a similar project in the next folder, and no access to the folders around), says it is going to look before it looks outside the project, goes on without asking again when the person asked for what the folder shows, asks when there is something to choose or when it cannot look, and creates nothing before the person answers | `python tooling/sessions/test_entry_skill.py` |
| [`sessions/test_start_interview.py`](sessions/test_start_interview.py) | A whole interview of a new project, in one session of several turns with a scripted person who never approves a document: the state passes `check_state.py` with the steps closed, the six fixed documents are ready, in the person's language and free of template leftovers, the plan has a spec per task that says how to test it, and every message opened with where the conversation was | `python tooling/sessions/test_start_interview.py` |
| [`sessions/test_status_skill.py`](sessions/test_status_skill.py) | The status skill answers "where are we?" from the state file in a new session (the step, the decision taken, the next question), reports a planted problem (a document the state calls ready that does not exist), says there is no project in an empty folder, and changes no file | `python tooling/sessions/test_status_skill.py` |
| [`sessions/test_research_skill.py`](sessions/test_research_skill.py) | The research skill in three situations: alone with the web open, it reads pages in the session, recommends one option by the criterion the person gave, names its sources with the date and creates no file; in a project with the web closed, it says it could not read the pages, recommends all the same by the criterion in the state and writes the research document with what is left to verify; with no criterion declared, it says which criteria it used. It never calls its own recommendation weak | `python tooling/sessions/test_research_skill.py` |
| [`sessions/test_decide_skill.py`](sessions/test_decide_skill.py) | The decide skill on one decision that is costly to undo, answered in three ways. It presents the recommendation before the other options, four at most, in a short message, and records nothing before the answer. Taking the recommendation records the decision with its reason, who decided, the date and the sources, and what was left to verify becomes an item of the test plan; deciding later records it as open and goes on; choosing against the recommendation records the person's choice, and the agent does not insist | `python tooling/sessions/test_decide_skill.py` |
| [`sessions/test_continue.py`](sessions/test_continue.py) | Continuing a project in a new session: stopped mid-step, the agent asks the question the state has as next and none that is answered, then closes the step, writes its document and moves on; with a state that is behind the files, it says so, shows what it rebuilt, asks to confirm and does not touch the state before that | `python tooling/sessions/test_continue.py` |
| [`sessions/test_codex.py`](sessions/test_codex.py) | Blueprint in Codex, the agent the skills were not written in: the CLI installs them for it, Codex finds the entry skill on its own and says which step the conversation is in, and a project started in Claude Code is continued from the question its state has as next. Runs `codex exec`, so it spends the account's ChatGPT quota, not the Claude one, and takes `--model` because a ChatGPT account refuses some models through Codex | `python tooling/sessions/test_codex.py` |
| [`sessions/test_personal_memory.py`](sessions/test_personal_memory.py) | What the record skill learns about the person, in three cases: told not to write outside the project, it does not and says the learning will not carry over; allowed but unable to reach the person's folder, it says so instead of reporting it saved; allowed and told where the folder is, it writes the preference there, with no content of the project, and the project's line in the list. A test session cannot write to the real `~/.blueprint/`, and that is on purpose | `python tooling/sessions/test_personal_memory.py` |
| [`sessions/test_setup_skill.py`](sessions/test_setup_skill.py) | Preparing a repository whose plan is closed, in three cases: an entry file that already exists keeps the person's rules and gains the Blueprint block; without one, the file is created and a team gets a playbook per role; and "let's go on" prepares the repository before the first task. Then the acceptance of FR-30: a new session **with Blueprint not loaded** is told to start the first task, and names the task, where it is written and where to record | `python tooling/sessions/test_setup_skill.py` |
| [`sessions/test_change_path.py`](sessions/test_change_path.py) | A change to a project that already exists, in three cases: a small change becomes one spec and nothing else; an improvement gets a plan with what enters, what changes and what leaves, with the document that matches the code left alone and the outdated part the change does not touch reported and not corrected; a reorganisation leaves the requirements untouched and writes what must keep working, the affected part as it is and as it will be, and the decision. In all three the agent reads the code first, writes nothing before the person answers, and changes no code | `python tooling/sessions/test_change_path.py` |

They are not among the checks to run before every change: they need Claude Code
on the PATH (the Codex one needs `codex` instead), take a few minutes (the interview about twenty) and spend model
usage, from the same account as your own sessions. Run the one for a skill after
changing that skill. When the account's usage limit is reached, a test says it
could not run and exits with 2, instead of reporting failures; the record skill's
test does not tell the two apart yet.

Every test but the record skill's ends with one line of what it took: the
turns, the minutes of agent time, the cost Claude Code reports at API prices
(on a subscription that is a measure of usage, not a charge), and the tool
calls that were refused. A turn that resumes a session reports the cost of the
whole session so far, so the turns of one session are counted once. One run of
the entry test is five sessions, about four minutes of agent time and under two
dollars at API prices; the whole interview is one session of seven or eight
turns, about fourteen minutes and three and a half dollars. Every test ends by
naming the checks that failed, so the last lines of its output are enough to
report a failure.

What the person says in each test is written in Portuguese, as someone
conducting an interview would write it: in [`sessions/record/`](sessions/record/)
for the record skill, and inside the test itself for the others. The projects a
test starts from are in Portuguese too, as that person's project would be: the
states in [`sessions/entry/`](sessions/entry/) and
[`sessions/decide/`](sessions/decide/), and two small projects with code that
runs in [`sessions/change/`](sessions/change/).

Every test but the record skill's, which still calls Claude Code on its own,
runs its sessions through [`sessions/harness.py`](sessions/harness.py), which
fences each session into its project folder: reading outside it is refused
unless the test grants a folder, which stands for the person giving access. A
session does not see the connectors (MCP servers) of the account that runs the
test: they have no part in what is tested, and their list alone costs tokens at
every session start. The harness reads what the agent said and did, in order. The words of a reply are a rough
check, so the test prints every reply in full for a person to read.
The entry test keeps what every session said and did, in the system's temporary
folder or where `--save FILE` says, and `--replay FILE` judges a kept run again
without spending a session: that is how to read a run that failed, and how to
work on the checks themselves. The interview test does the same with
`--folder DIR`: the same command on a finished run only judges it again.
