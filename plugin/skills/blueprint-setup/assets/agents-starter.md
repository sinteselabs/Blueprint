<!-- The block the CLI writes into a project's AGENTS.md when Blueprint is
installed, before there is anything to describe. It is written in English,
because nobody has said yet which language this project's documents are in.
The `blueprint-setup` skill replaces what is between the marks once the
documents exist, in the project's own language. The two marks stay as they are:
they are what the next session finds. -->

<!-- blueprint:start -->
## Blueprint

This project has Blueprint installed, and has not been through it yet.

To start, open your coding agent in this folder and say what you want to do, in
your own words: start something new, continue, improve or reorganise what is
here. The agent works out where to begin and asks one block of questions at a
time.

| What | Where |
|---|---|
| The method, as agent skills | `.claude/skills/` and `.agents/skills/` |
| Where the project is, once it starts | `.blueprint/state.md` |
| What was installed, and in which version | `.blueprint/installed.json` |

Until the interview starts, there is nothing else here to read. What replaces
this block will say where the documents, the plan and the journal are.
<!-- blueprint:end -->
