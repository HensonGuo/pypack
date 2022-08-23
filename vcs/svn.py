import os
from utils.util import Util
from utils.config import LOCAL_DEBUG


class Svn(object):
    def __init__(self, url, path):
        self.url = url
        self.path = path
        self.commit_version = ""

    def pull(self):
        if os.path.isdir(self.path):
            print(f"repo {self.path} in local.")
            return 0
        parent_dir = os.path.dirname(self.path)
        if not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)
        args = ['checkout', self.url, self.path]
        print(f'> svn checkout {self.url} {self.path}')
        ret, _, __ = Util.svn(args, os.getcwd(), redirect=True)
        return ret

    def checkout_version(self, version):
        if os.path.isdir(self.path):
            print(f"repo {self.path} in local.")
            return 0
        args = ['checkout', "-r", str(version), self.url, self.path]
        print(f'> svn checkout -r {version} {self.url} {self.path}')
        ret, _, __ = Util.svn(args, os.getcwd(), redirect=True)
        return ret

    def update(self):
        # 可能被锁，所以先reset下
        ret = self.reset()
        if ret != 0:
            return ret
        args = ['up']
        print(f'> svn update {self.path}')
        ret, _, __ = Util.svn(args, self.path)
        return ret

    def reset(self):
        args = [["cleanup"],
                ["revert", "-R", "."],
                ["cleanup", "--remove-unversioned", "."]]
        for arg in args:
            ret, _, _ = Util.svn(arg, self.path)
            if ret != 0:
                return ret
        return 0

    def push(self, comment, timeout=300):
        if LOCAL_DEBUG:
            return 0
        if '\n' not in comment:
            ret, out, err = Util.svn(['commit', '-m', comment + " "], self.path)
            pos = out.find("Committed revision ")
            self.commit_version = out[pos + len("Committed revision "): out.find(".", pos)]
            return ret
        else:
            import tempfile
            fn = tempfile.mktemp()
            fp = open(fn, 'w', encoding="gbk")
            fp.write(comment)
            fp.close()
            ret, out, err = Util.svn(['commit', '-F', fn, '--encoding', "gbk"], self.path, timeout=timeout)
            pos = out.find("Committed revision ")
            self.commit_version = out[pos + len("Committed revision "): out.find(".", pos)]
            return ret

            if os.path.exists(fn):
                os.remove(fn)
        return 1

    def get_version(self):
        assert not "svn not supported"

    def get_commit_version(self):
        return self.commit_version

    def get_lastest_version(self):
        args = ["log", "-l 1", "-q"]
        _, out, err = Util.svn(args, self.path)
        line = out.split("\n")[1]
        reversion = line[1:line.find(" ")]
        return reversion