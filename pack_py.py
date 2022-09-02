# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
import zipfile
import shutil
import compileall
import json
import time
import datetime
import argparse

from vcs.git import Git
from change_imports import changeImports

class PackPyc(object):

    def __init__(self):
        self.local_pack = False
        self.git_branch = ""
        self.workspace = ""
        self.out_dir = ""
        self.src_dir = ""

    def copySrc2Temp(self, temp_dir, verison):
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.mkdir(temp_dir)
        dst_dir = os.path.join(temp_dir, "{}_r{}/".format(self.repo_name, verison))
        shutil.copytree(self.src_dir, dst_dir, ignore=shutil.ignore_patterns(".git"))
        init_file = dst_dir + "__init__.py"
        f = open(init_file, "w")
        f.close()

    def makeResName(self, version):
        return '{}-{}-{}.res'.format(self.repo_name, self.git_branch, version)

    def packpyd_dir(self, pzp, pyd_dir, target_dir):
        for root, dirs, files in os.walk(pyd_dir):
            for file in files:
                if file.endswith("pyd"):
                    filePath = os.path.join(root, file)
                    targetFilePath = os.path.join(target_dir, file)
                    pzp.write(filePath, targetFilePath)

    def joinSrcPath(self, path):
        return os.path.join(self.src_dir, path)

    def writeExtraPzp(self, pzp):
        # 写第三方依赖库third-party
        pass

    def makeRes(self, temp_dir, version):
        cur_dir = os.getcwd()
        os.chdir(self.out_dir)
        suc = compileall.compile_dir("./pack_temp/")
        assert suc and "打包失败"
        os.chdir(cur_dir)

        pyc_dir_name = "{}_r{}".format(self.repo_name, version)
        res_name = os.path.join(self.out_dir, self.makeResName(version))
        pyc_dir = os.path.join(temp_dir, pyc_dir_name)
        print(res_name)
        pzp = zipfile.PyZipFile(res_name, "w")
        pzp.writepy(pyc_dir)

        self.writeExtraPzp(pzp)

        # 2. 时间戳
        now_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        version_date = time.strftime("%Y%m%d%H%M%S", time.localtime(int(version)))
        version_file = "{}_{}_{}_{}".format(self.git_branch, version, version_date, now_date)
        print(version_file)
        with open(version_file, "w") as f:
            pass
        pzp.write(version_file, os.path.basename(version_file))
        os.remove(version_file)
        pzp.close()
        return os.path.normpath(os.path.abspath(res_name))

    def packRes(self):
        config = {}
        if self.local_pack:
            version = 100
        else:
            version = self.repo.get_version()

        # 有变化才打包
        res_name = '{}-{}-{}.res'.format(self.repo_name, self.git_branch, version)
        if self.rebuild:
            print("force rebuild")
            need_pack = True
        else:
            need_pack = not os.path.exists(os.path.join(self.out_dir, res_name))
        if need_pack:
            temp_dir = os.path.join(self.out_dir, "./pack_temp/")

            # 把代码拷贝到pack_temp目录
            self.copySrc2Temp(temp_dir, version)

            # 更改目录
            dst_dir = os.path.join(temp_dir, "{}_r{}/".format(self.repo_name, version))
            items = os.listdir(dst_dir)
            root_packges = []
            for item in items:
                if os.path.isdir(f"{dst_dir}/{item}"):
                    root_packges.append(item)
            changeImports(temp_dir, "{}_r{}".format(self.repo_name, version), root_packges)

            # 制作res
            res_path = self.makeRes(temp_dir, version)

            # 清除临时文件
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

            config["build"] = 1
            config["res"] = res_path
            config["revision"] = version
        else:
            config["build"] = 0
            print("{} already packed.".format(res_name))
        return config

    def build(self, repoUrl, branch, workspace, rebuild):
        self.repo_name = repoUrl[repoUrl.rfind("/") + 1:].replace(".git", "").lower()
        self.git_branch = branch
        self.local_pack = branch == "local"
        self.rebuild = rebuild
        self.workspace = workspace

        # 创建工作目录
        self.src_dir = os.path.join(self.workspace, "src_{}".format(self.git_branch))
        self.out_dir = os.path.join(self.workspace, "out_{}".format(self.git_branch))
        self.repo = Git(repoUrl, self.src_dir, branch)
        try:
            if not os.path.exists(self.workspace):
                os.makedirs(self.workspace)
            if not os.path.exists(self.out_dir):
                os.makedirs(self.out_dir)
        except Exception as e:
            import traceback
            print("failed to create workspace for build.", file=sys.stderr)
            print(traceback.format_exc())
            return

        if branch == "local":  # 本地源码构建
            self.src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print(self.src_dir)
        else:  # 拉取源码构建
            print("clone git repo.")
            if not os.path.isdir(self.src_dir):
                self.repo.pull()

            if not os.path.isdir(os.path.join(self.src_dir, ".git")):
                print("failed to clone git repo.", file=sys.stderr)
                return

            print("update git repo.")
            self.repo.update()
            self.repo.reset()

        print("pack res/zip")
        config_reszip = self.packRes()
        config = {
            "res": config_reszip
        }
        config_txt = os.path.join(self.out_dir, "config.txt")
        with open(config_txt, "w") as f:
            f.write(json.dumps(config, indent=2))


def get_args(argv):
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--repourl", type=str, dest="repourl", required=True, help="git repo url")
    parser.add_argument("--branch", type=str, dest="branch", required=True, help="git repo branch")
    parser.add_argument("--workspace", type=str, dest="workspace", required=True, help="local path")
    parser.add_argument("--rebuild", type=int, dest="rebuild", required=True, help="rebuild")
    args = parser.parse_args(argv)
    return args


def run(builderClass):
    args = get_args(sys.argv[1:])
    builder = builderClass()
    builder.build(args.repourl, args.branch, args.workspace, args.rebuild)
