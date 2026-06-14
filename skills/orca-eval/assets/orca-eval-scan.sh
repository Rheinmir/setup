#!/usr/bin/env bash
set -euo pipefail

N=${1:-1}

slug=$(echo "$PWD" | tr '/.' '-' | sed 's/^-//')
dir="$HOME/.claude/projects/-${slug}"

if [ ! -d "$dir" ]; then
  echo "ERROR: session dir not found" >&2
  exit 1
fi

# use array from ls
files=()
while IFS= read -r -d '' f; do
  files+=("$f")
done < <(find "$dir" -maxdepth 1 -name '*.jsonl' -type f -exec stat -f "%m %N" {} \; | sort -rn | head -n "$N" | awk '{for(i=2;i<=NF;i++) printf "%s%s", (i>2?OFS:""), $i; print "\0"}')
# fallback: read newline-separated
if [ ${#files[@]} -eq 0 ]; then
  while IFS= read -r f; do
    files+=("$f")
  done < <(ls -1t "$dir"/*.jsonl 2>/dev/null | head -n "$N")
fi

if [ ${#files[@]} -eq 0 ]; then
  echo "ERROR: session dir not found" >&2
  exit 1
fi

for f in "${files[@]}"; do
  fname=$(basename "$f")
  mtime=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$f" 2>/dev/null || echo "?")
  echo "=== SESSION $fname ($mtime) ==="
  python3 -c "
import json, sys
from collections import Counter

fpath = '$f'
prompts = []
errors = []
bash_cmds = []
cmd_counts = Counter()

with open(fpath) as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        typ = obj.get('type')
        if typ == 'user':
            msg = obj.get('message', {})
            content = msg.get('content', '')
            if isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    # text prompt
                    if item.get('type') == 'text' and 'text' in item:
                        t = item['text'][:200]
                        if t:
                            prompts.append(t)
                    # tool result - check errors
                    if item.get('type') == 'tool_result' or 'tool_use_id' in item:
                        is_err = item.get('is_error')
                        c = item.get('content', '') or ''
                        if isinstance(c, list):
                            c = ' '.join(str(x) for x in c)
                        if isinstance(c, str) and is_err:
                            errors.append(c[:150])
            elif isinstance(content, str) and content.strip():
                prompts.append(content.strip()[:200])
        elif typ == 'assistant':
            msg = obj.get('message', {})
            content = msg.get('content', [])
            if isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    if item.get('type') == 'tool_use' and item.get('name') == 'Bash':
                        cmd = item.get('input', {}).get('command', '') or ''
                        cmd = cmd.strip()
                        if cmd:
                            bash_cmds.append(cmd)
                            cmd_counts[cmd] += 1

# Deduplicate prompts while preserving order
seen = set()
uniq_prompts = []
for p in prompts:
    if p not in seen:
        seen.add(p)
        uniq_prompts.append(p)

print('PROMPTS:')
if uniq_prompts:
    for p in uniq_prompts:
        # sanitize
        safe = p.replace('\\\\n', ' ').replace('\\n', ' ').replace('\n', ' ').replace('\r','')
        print(f'  {safe}')
else:
    print('  (none)')

print()
print('ERRORS:')
if errors:
    for e in errors:
        safe = e.replace('\\\\n', ' ').replace('\\n', ' ').replace('\n', ' ').replace('\r','')
        print(f'  {safe}')
else:
    print('  (none)')

print()
print('REPEATED COMMANDS:')
repeated = [(c, n) for c, n in cmd_counts.items() if n >= 3]
repeated.sort(key=lambda x: -x[1])
if repeated:
    for cmd, count in repeated:
        safe = cmd.replace('\\\\n', ' ').replace('\\n', ' ').replace('\n', ' ').replace('\r','')
        safe = safe[:120]
        print(f'  ({count}x) {safe}')
else:
    print('  (none)')
"
  echo ""
done
