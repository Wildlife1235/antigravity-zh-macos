#!/usr/bin/env python3
"""Experimental local installer for Antigravity 2.34.0 on macOS."""
import argparse
import datetime
import hashlib
import os
from pathlib import Path
import plistlib
import shutil
import signal
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
APP = Path('/Applications/Antigravity.app')
DATA = Path.home() / 'Library/Application Support/Antigravity-ZH-macOS'
VERSION = '2.34.0'

def run(*args, **kwargs):
    return subprocess.run([str(x) for x in args], check=True, **kwargs)

def version(app):
    return plistlib.loads((app/'Contents/Info.plist').read_bytes())['CFBundleShortVersionString']

def signed_official(app):
    run('codesign', '--verify', '--deep', '--strict', app)
    result = run('codesign', '-dv', app, capture_output=True, text=True)
    if 'TeamIdentifier=EQHXZ8M8AV' not in result.stderr:
        raise RuntimeError('应用不是已验证的 Google 签名原版，停止操作。')

def app_pids(app):
    executable = str(app/'Contents/MacOS/Antigravity')
    output = run('ps', '-axo', 'pid=,comm=', capture_output=True, text=True).stdout
    return [int(line.strip().split(None, 1)[0]) for line in output.splitlines()
            if len(line.strip().split(None, 1)) == 2 and line.strip().split(None, 1)[1] == executable]

def stop(app):
    for pid in app_pids(app):
        os.kill(pid, signal.SIGTERM)
    for _ in range(40):
        if not app_pids(app):
            return
        time.sleep(.25)
    raise RuntimeError('应用未退出，停止操作。')

def start(app):
    run('open', app)
    time.sleep(8)
    if not app_pids(app):
        raise RuntimeError('应用未能保持运行。')

def sign(target, entfile):
    raw = run('codesign', '-d', '--entitlements', ':-', target, capture_output=True).stdout
    ent = plistlib.loads(raw) if raw.strip() else {}
    ent['com.apple.security.cs.disable-library-validation'] = True
    entfile.write_bytes(plistlib.dumps(ent))
    run('codesign', '--force', '--sign', '-', '--options', 'runtime', '--entitlements', entfile, target)

def apply(app):
    if version(app) != VERSION:
        raise RuntimeError(f'仅验证版本 {VERSION}；当前版本不匹配。')
    signed_official(app)
    DATA.mkdir(parents=True, exist_ok=True)
    work = DATA / ('run-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    work.mkdir()
    backup = work/'Antigravity-original.app'
    original = app/'Contents/Resources/app.asar'
    original_sha = hashlib.sha256(original.read_bytes()).hexdigest()
    run(sys.executable, ROOT/'build_offline.py', original, work/'build')
    if hashlib.sha256(original.read_bytes()).hexdigest() != original_sha:
        raise RuntimeError('构建期间应用发生更新，未修改应用。')
    print('即将关闭应用，请确认已保存所有工作。', flush=True)
    stop(app)
    if hashlib.sha256(original.read_bytes()).hexdigest() != original_sha:
        raise RuntimeError('应用已变化，未修改应用。')
    run('ditto', app, backup)
    signed_official(backup)
    archive = work/'build/app.asar'
    try:
        shutil.copy2(archive, original)
        with archive.open('rb') as f:
            n = struct.unpack('<4I', f.read(16))[3]
            digest = hashlib.sha256(f.read(n)).hexdigest()
        info = app/'Contents/Info.plist'
        obj = plistlib.loads(info.read_bytes())
        obj['ElectronAsarIntegrity']['Resources/app.asar']['hash'] = digest
        info.write_bytes(plistlib.dumps(obj, sort_keys=False))
        for i, helper in enumerate(sorted((app/'Contents/Frameworks').glob('*.app'))):
            sign(helper, work/f'helper-{i}.plist')
        sign(app, work/'main.plist')
        run('codesign', '--verify', '--deep', '--strict', app)
        start(app)
        print(f'已安装。官方备份：{backup}')
    except BaseException:
        stop(app)
        run('ditto', backup, app)
        signed_official(app)
        run('open', app)
        print(f'安装失败，已恢复官方备份：{backup}', file=sys.stderr)
        raise

def restore(app, backup):
    signed_official(backup)
    if version(app) != version(backup):
        raise RuntimeError('应用与备份版本不同，拒绝覆盖。')
    stop(app)
    run('ditto', backup, app)
    signed_official(app)
    start(app)
    print('已恢复官方版。')

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='action', required=True)
    sub.add_parser('install')
    r = sub.add_parser('restore')
    r.add_argument('--backup', type=Path, required=True, help='安装时输出的官方备份 .app 路径')
    args = p.parse_args()
    if sys.platform != 'darwin':
        p.error('仅支持 macOS')
    if args.action == 'install':
        apply(APP)
    else:
        restore(APP, args.backup.expanduser().resolve(strict=True))

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'错误：{exc}', file=sys.stderr)
        sys.exit(1)
