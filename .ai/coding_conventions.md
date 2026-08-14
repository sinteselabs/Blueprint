# Coding Conventions

<!--
  The standards an assistant MUST follow when writing code in this repo. Be specific
  and prescriptive — versions, tools, patterns, naming. Delete sections that don't
  apply to your stack and add ones that do.
-->

## {{Language / Framework}}

- **Version:** {{e.g. Dart 3+ / Python 3.12+ / TS 5 strict}}
- **Lints / formatting:** {{tooling + config}}
- **State / architecture pattern:** {{e.g. Riverpod, layered repositories}}
- **Models / validation:** {{e.g. freezed, Pydantic v2, Zod}}
- **Error handling:** {{how errors flow — typed results, no leaking exceptions to UI}}

### {{Sub-area, e.g. "API specifics" / "Component conventions"}}

- {{rule}}

### Example

```{{lang}}
{{A short, canonical code example showing the preferred style.}}
```

---

## Data / Database

- {{migrations, IDs, naming, indexing rules}}

---

## Testing

- **Unit:** {{what + tools}}
- **Integration / widget:** {{what + tools}}
- **Rules / security:** {{if applicable}}

---

## Git

- Branch naming: `feat/`, `fix/`, `chore/`, `infra/` prefixes
- Commit messages: conventional commits — `feat(scope): summary`
- No secrets committed; use `.env.example` with placeholders
- Parallel agents work in separate worktrees under `.worktrees/` (git-ignored),
  one branch each — see [workflows/parallel-agents.md](workflows/parallel-agents.md)

---

## Security

- No secrets in source — environment variables / secret managers only
- {{parameterised queries / input validation / authz rules / PII handling}}

---

## Naming

- Files: {{convention}}
- Types / classes: {{convention}}
- {{other naming rules}}
