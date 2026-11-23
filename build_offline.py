#!/usr/bin/env python3
"""Build an inspectable localization archive; never modify an installed app."""
import argparse
import json
from pathlib import Path
import subprocess

import asar
import translate as upstream


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('original', type=Path)
    parser.add_argument('output', type=Path, help='new, empty output directory')
    args = parser.parse_args()
    original = args.original.resolve(strict=True)
    output = args.output.resolve()
    if output.exists():
        parser.error('output must not exist')
    output.mkdir(parents=True)
    extracted = output / 'extracted'
    extracted.mkdir()
    unpacked = upstream.original_unpacked_set(str(original))
    asar.extract(str(original), str(extracted))
    pkg = json.loads((extracted / 'package.json').read_text(encoding='utf-8'))
    if pkg.get('version') != '2.34.0':
        raise SystemExit('Only Antigravity 2.34.0 has been targeted; stopped.')
    dictionary = upstream.load_dictionary()
    patched = []
    for rel in ('dist/preload.js', 'dist/ideInstall/wizardPreload.js'):
        target = extracted / rel
        if target.exists():
            upstream.apply_blocks(str(target), [('engine', upstream.build_engine_block(dictionary))], engine=True)
            patched.append((rel, upstream.BLOCK_BEGIN % 'engine'))
    if not any(rel == 'dist/preload.js' for rel, _ in patched):
        raise SystemExit('Missing preload entry; stopped.')
    for rel, blocks in [('dist/menu.js', [('menu', upstream.build_menu_block())]),
                        ('dist/main.js', [('menu', upstream.build_menu_block()), ('dialog', upstream.build_dialog_block())])]:
        target = extracted / rel
        if target.exists():
            upstream.apply_blocks(str(target), blocks)
            patched.extend((rel, upstream.BLOCK_BEGIN % name) for name, _ in blocks)
    upstream.patch_loading_overlay(str(extracted))
    for rel in sorted({rel for rel, _ in patched}):
        subprocess.run(['node', '--check', str(extracted / rel)], check=True)
    archive = output / 'app.asar'
    asar.pack(str(extracted), str(archive), upstream.UNPACK_PATTERNS, exact_unpack=unpacked)
    ok, reason = upstream.verify_new_asar(str(archive), str(extracted), patched, unpacked)
    if not ok:
        raise SystemExit(reason)
    print(f'Built {archive}; version={pkg["version"]}; dictionary={len(dictionary)}; files={len(asar.list_files(str(archive)))}')
    print('Offline prototype only: not installed or signed.')


if __name__ == '__main__':
    main()
