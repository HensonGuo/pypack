import os
from utils.util import Util


class Git(object):
    def __init__(self, url, path, branch):
        self.url = url
        self.branch = branch
        self.path = path

    def pull(self):
        if os.path.isdir(self.path):
            if not os.listdir(self.path):
                print(f"repo {self.path} empty, remov.e")
                os.rmdir(self.path)
            else:
                print(f"repo {self.path} in local, skip.")
                return 0
        parent_dir = os.path.dirname(self.path)
        if not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)
        args = ['clone', '-b', self.branch, self.url, self.path]
        print(f'> git clone {self.url} {self.path}')
        return Util.git(args, os.getcwd())[0]

    def update(self):
        print(f'> git update {self.path}')
        args = ['fetch', '-f', '-q', '-a', '-v']
        ret, _, __ = Util.git(args, self.path)
        if ret != 0:
            return ret
        args = ['remote', 'update', 'origin', '--prune']
        ret, _, __ = Util.git(args, self.path)
        if ret != 0:
            return ret
        return self.reset()

    def reset(self):
        arg = ["reset", "--hard", f"origin/{self.branch}"]
        ret, _, _ = Util.git(arg, self.path)
        return ret

    def push(self, comment, timeout=300):
        from utils.config import LOCAL_DEBUG
        args = [["add", "-u"], ["commit", f"-m {comment}"]]
        if not LOCAL_DEBUG:
            args.append(["push"])
        ret = 0
        for arg in args:
            ret, _, _ = Util.git(arg, self.path)
            if ret != 0:
                print(f"{arg[0]} git repo failed.")
                return 1
        return ret

    def get_version(self):
        _, out, _ = Util.git(["log", "-1", "--pretty=%at"], self.path)
        version = out.strip('\n')
        if not version:
            return "0"
        return version

    def get_subdir_version(self, subdir):
        subdir = os.path.join(self.path, subdir)
        assert os.path.isdir(subdir)
        _, out, _ = Util.git(["log", "-1", "--pretty=%at"], subdir)
        version = out.strip('\n')
        if not version:
            return "0"
        return version

    def get_hash(self):
        _, out, _ = Util.git(["log", "-1", "--pretty=%H"], self.path)
        long_hash = out.strip('\n')
        _, out, _ = Util.git(["log", "-1", "--pretty=%h"], self.path)
        short_hash = out.strip('\n')
        return long_hash, short_hash

    def get_last_comment(self, count):
        args = ["log", "--format=%cN: %s", "--decorate", f"-n {count}"]
        _, out, err = Util.git(args, self.path)
        return out

    def get_all_remote_branches(self):
        args = ["branch", "-a"]
        _, out, err = Util.git(args, self.path)
        branches = []
        for branch in out.split("\n"):
            branch = branch.strip("\r\n").strip("\n").strip(" ")
            if branch.startswith("remotes/origin/"):
                branches.append(branch)
        return branches

    def sync_remote_branches(self):
        args = ['remote', 'update', 'origin', '--prune']
        _, out, err = Util.git(args, self.path)

    def get_modified_files(self, start, to):
        args = ["log", r'--format=', "--decorate", "--ancestry-path", f"{start}..{to}", "--name-only"]
        _, out, err = Util.git(args, self.path)
        out = out.strip("\n")
        return out.split("\n")

    def get_log(self, limit, subdir=None):
        args = ["log", "--format=[tag-begin]【%ci %cN】\n %s", "--decorate", f"-n {limit}", "--name-only"]
        if subdir:
            args.append(subdir)
        _, out, err = Util.git(args, self.path)
        out = out.replace("[tag-begin]", "\n\n").strip("\n")
        out = out.replace("\n", "<br/>")
        return out

    def get_logs(self, start, to):
        args = ["log", "--format=%cN: %s", "--decorate", "--ancestry-path", f"{start}..{to}"]
        _, out, err = Util.git(args, self.path)
        return out