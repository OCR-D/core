import os
import re
import signal
import sys
from pathlib import Path
from time import time
from typing import List, Optional


def kill_mets_server_zombies(minutes_ago: Optional[int], dry_run: Optional[bool]) -> List[int]:
    if minutes_ago is None:
        minutes_ago = 90
    if dry_run is None:
        dry_run = False

    now = time()
    cmdline_pat = r'.*ocrd workspace -U.*server start $'
    ret = []
    for procdir in sorted(Path('/proc').glob('*'), key=os.path.getctime):
        if not procdir.is_dir():
            continue
        cmdline_file = procdir.joinpath('cmdline')
        if not cmdline_file.is_file():
            continue
        ctime_ago = int((now - procdir.stat().st_ctime) / 60)
        if ctime_ago < minutes_ago:
            continue
        cmdline = cmdline_file.read_text().replace('\x00', ' ')
        if re.match(cmdline_pat, cmdline):
            pid = int(procdir.name)
            ret.append(pid)
            print(
                f'METS Server with PID {pid} was created {ctime_ago} minutes ago, more than {minutes_ago}, '
                f'so killing (cmdline="{cmdline})',
                file=sys.stderr
            )
            if dry_run:
                print(f'[dry_run is active] kill {pid}')
            else:
                os.kill(pid, signal.SIGTERM)
    return ret