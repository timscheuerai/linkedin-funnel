#!/usr/bin/env python3
"""Check this distributable template without installing dependencies."""

import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
errors = []


def require(condition, message):
    if not condition:
        errors.append(message)


catalog = json.loads((ROOT / 'skills/catalog.json').read_text())['skills']
names = [skill['name'] for skill in catalog]
require(len(names) == len(set(names)), 'Duplicate skill names in catalog')
actual = {path.parent.name for path in (ROOT / 'skills').glob('*/SKILL.md')}
require(set(names) == actual, 'Catalog does not match bundled skills')

for skill in catalog:
    path = ROOT / skill['path']
    require(path == ROOT / 'skills' / skill['name'] / 'SKILL.md',
            f"Unexpected skill path: {skill['path']}")
    if not path.exists():
        errors.append(f'Missing skill: {path}')
        continue
    frontmatter = re.match(r'\A---\n(.*?)\n---(?:\n|$)', path.read_text(), re.S)
    require(frontmatter is not None, f'Missing skill frontmatter: {path}')
    if frontmatter:
        for key in ('name', 'description'):
            match = re.search(rf'^{key}: (.+)$', frontmatter[1], re.M)
            require(match is not None and match[1] == skill[key],
                    f'Catalog {key} mismatch: {path}')

for alias in ('.agents/skills', '.claude/skills'):
    require((ROOT / alias).is_symlink(), f'Missing discovery symlink: {alias}')
    require((ROOT / alias).resolve() == ROOT / 'skills', f'Wrong skill target: {alias}')

for folder in (ROOT, ROOT / 'context'):
    require((folder / 'AGENTS.md').read_text() == (folder / 'CLAUDE.md').read_text(),
            f'Agent instructions diverge in {folder}')

# Skip fenced examples; context wiki links are checked by its own linter.
for path in ROOT.rglob('*.md'):
    if '.git' in path.parts:
        continue
    text = re.sub(r'^```.*?^```[^\n]*$', '', path.read_text(), flags=re.M | re.S)
    for target in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', text):
        target = target.strip('<>')
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        linked = (path.parent / unquote(parsed.path)).resolve()
        require(linked.is_relative_to(ROOT), f'Link escapes template: {path}: {target}')
        require(linked.exists(), f'Broken local link: {path.relative_to(ROOT)}: {target}')

json_files = [p for p in ROOT.rglob('*.json') if '.git' not in p.parts]
for path in json_files:
    try:
        json.loads(path.read_text())
    except (ValueError, UnicodeError) as error:
        errors.append(f'Invalid JSON {path.relative_to(ROOT)}: {error}')

manifest = json.loads((ROOT / 'assets/manifest.json').read_text())
for asset in manifest['assets']:
    path = ROOT / 'assets' / asset['file']
    require(path.exists(), f'Missing asset: {path.name}')
    if path.exists():
        require(hashlib.sha256(path.read_bytes()).hexdigest() == asset['sha256'],
                f'Asset hash differs: {path.name}')

if errors:
    print('\n'.join(errors), file=sys.stderr)
    sys.exit(1)
print(f'Template OK: {len(names)} skills, discovery links, local links, '
      f'{len(json_files)} JSON files and {len(manifest["assets"])} asset hashes')
