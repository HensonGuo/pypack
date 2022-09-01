# -*- coding: utf-8 -*-
from __future__ import print_function
from pack_py import PackPyc, run


class TestBuilder(PackPyc):
    def __init__(self):
        super(TestBuilder, self).__init__()

    def writeExtraPzp(self, pzp):
        pass


if __name__ == "__main__":
    import sys
    sys.argv = []
    sys.argv.append("")
    sys.argv.append("--repourl")
    sys.argv.append("git@github.com:HensonGuo/TcpLinkProtocols.git")
    sys.argv.append("--branch")
    sys.argv.append("master")
    sys.argv.append("--workspace")
    sys.argv.append(r"F:\test")
    sys.argv.append("--rebuild")
    sys.argv.append("1")
    run(TestBuilder)