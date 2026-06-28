# wiki/sources/evals — WikiEval goldens

Each `*.md` file here is a **golden** for the WikiEval suite
(`harness/scripts/wikieval.py`). The YAML frontmatter is the machine-read contract:

| key        | required | meaning |
|------------|----------|---------|
| `id`       | no       | golden id (defaults to the filename stem); referenced by `outputs.json` |
| `input`    | yes\*    | the prompt / question |
| `expected` | yes\*    | the reference answer (used by the optional tier-2 similarity) |
| `rubric`   | no       | instructions for the tier-3 LLM judge (the quarantined adapter) |
| `asserts`  | no       | tier-1 deterministic checks (the build-now core) |

\* a file is treated as a golden if it has frontmatter with at least one of
`input` / `expected` / `asserts`.

Assert forms (quote them so YAML keeps backslashes and colons literal):
`contains:foo` · `icontains:foo` · `not-contains:foo` · `equals:bar` ·
`regex:^...$` · `is-json` · `is-sql-ish`.

These files also obey the wiki rules: every golden needs valid frontmatter with a
non-empty `type` (R9) and an `## Origin` section (R2). `README.md` and `_template.md`
are skipped by both the validators and the eval loader.

Run the suite with a fixed candidate set (no model needed):

```sh
python3 harness/scripts/wikieval.py --outputs harness/evals/wikieval-outputs.example.json
```
