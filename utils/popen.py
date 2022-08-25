# 对subprocess.Popen的简易封装，实时输出进程日志
import os
import sys
import subprocess
from utils.util import Util


def Popen(cmd, cwd, logger=None, shell=False, env=None):
    if not logger:
        logger = sys.stdout
    logger.write(f'> {subprocess.list2cmdline(cmd)}\n')
    p = subprocess.Popen(cmd,
                         shell=shell,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         cwd=cwd,
                         env=env if env else os.environ)
    while True:
        buf = p.stdout.readline()
        if not buf:
            break

        line = Util.to_unicode(buf)
        logger.write(line)

    ret = p.wait()
    if p.stdout:
        p.stdout.close()
    if p.stderr:
        p.stderr.close()
    return ret


def test_windows_cmd():
    import os
    cmd = ["tree", "/f"]
    Popen(cmd, os.getcwd(), shell=True)


def test_git_clone():
    import os
    cmd = ["git", "clone", "git@github.com:HensonGuo/TcpLinkProtocols.git",
           r"F:\TcpLinkProtocols"]
    Popen(cmd, os.getcwd(), shell=False)


if __name__ == "__main__":
    # test_windows_cmd()
    test_git_clone()
