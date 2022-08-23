import os
import json
import subprocess
import datetime
from pathlib import Path


class Util(object):
    @staticmethod
    def to_unicode(raw):
        if not raw:
            return ""

        if isinstance(raw, type("")):
            return raw

        assert isinstance(raw, bytes)

        encodings = ["utf-8", "gbk"]
        u = raw
        for encoding in encodings:
            match = True
            try:
                u = raw.decode(encoding)
            except UnicodeDecodeError as e:
                match = False
            if match:
                u = u.replace("\r\n", "\n")
                break
        if not isinstance(u, str):
            print(f"cannot decode bytes to unicode using encodings as follows: {encodings}\n{raw}")
            u = repr(raw)
        return u

    @staticmethod
    def execute(exe, cmd, cwd, timeout=None):
        if exe:
            cmd.insert(0, exe)
        print(f'> {subprocess.list2cmdline(cmd)}')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)
        stdout, stderr = p.communicate(timeout=timeout)
        print(p.returncode)
        print(Util.to_unicode(stdout))
        print(Util.to_unicode(stderr))
        return p.returncode, Util.to_unicode(stdout), Util.to_unicode(stderr)

    @staticmethod
    def execute_no_redirect(exe, cmd, cwd, timeout=None):
        cmd.insert(0, exe)
        print(f'> {subprocess.list2cmdline(cmd)}')
        p = subprocess.Popen(cmd, cwd=cwd)
        retcode = p.wait(timeout)
        print(retcode)
        return retcode

    @staticmethod
    def svn(cmd, cwd, timeout=None, redirect=True):
        svn = str(Util.join_path("tools/svn/svn.exe"))
        return Util.execute("svn.exe", cmd, cwd, timeout) if redirect else Util.execute_no_redirect("svn.exe", cmd, cwd, timeout)

    @staticmethod
    def git(cmd, cwd):
        return Util.execute('git.exe', cmd, cwd)

    @staticmethod
    def join_path(relpath):
        return Path(__file__).absolute().parent.parent.joinpath(relpath).resolve()

    # 获取输出目录，存储pdb和log
    @staticmethod
    def get_output_dir():
        output = Util.join_path("../cc_client_builder_output")
        if not output.is_dir():
            output.mkdir(parents=True)
        return output

    @staticmethod
    def get_log_dir():
        log_dir = Util.join_path("tmp/logs")
        if not log_dir.is_dir():
            log_dir.mkdir(parents=True)
        return log_dir

    @staticmethod
    def prepare_log(name):
        now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        log_name = f"{name}-{now}"
        log_save_dir = Util.get_output_dir().joinpath("build_log")
        if not os.path.exists(log_save_dir):
            os.makedirs(log_save_dir)
        log_path = log_save_dir.joinpath(log_name)
        return open(log_path, "w", encoding="utf-8", newline='\n', buffering=1), log_name

    @staticmethod
    def record_build_hash(target, hash, sub_versions={}):
        '''
        记录本次打包时源码最新提交的hash
        '''
        hash_file = Util.join_path("tmp/build_hash.json")
        if not os.path.exists(hash_file):
            with open(hash_file, "w") as f:
                f.write(json.dumps({}))
        with open(hash_file, "r") as f:
            data = json.loads(f.read())
        if target in data:
            data[target].update({"hash": hash})
        else:
            data[target] = {"hash": hash}
        data[target]["submodules"] = {}
        for name, _hash in sub_versions.items():
            data[target]["submodules"][name] = {"hash": _hash}
        with open(hash_file, "w") as f:
            f.write(json.dumps(data, indent=2))

    @staticmethod
    def get_last_build_hash(target):
        '''
        获取上次打包时源码最新提交的hash
        '''
        DEFAULT_LAST_HASH = "HEAD^^^^^"
        hash_file = Util.join_path("tmp/build_hash.json")
        if not os.path.exists(hash_file):
            return DEFAULT_LAST_HASH
        with open(hash_file, "r") as f:
            data = json.loads(f.read())
        if target not in data:
            return DEFAULT_LAST_HASH
        return data[target]["hash"]

    @staticmethod
    def get_submodule_last_build_hash(target, submodule):
        '''
        获取上次打包时源码最新提交的hash
        '''
        DEFAULT_LAST_HASH = "HEAD^^^^^"
        hash_file = Util.join_path("tmp/build_hash.json")
        if not os.path.exists(hash_file):
            return DEFAULT_LAST_HASH
        with open(hash_file, "r") as f:
            data = json.loads(f.read())
        if target not in data:
            return DEFAULT_LAST_HASH
        data = data[target]
        if "submodules" not in data:
            return DEFAULT_LAST_HASH
        data = data["submodules"]
        if submodule not in data:
            return DEFAULT_LAST_HASH
        return data[submodule]["hash"]