import os
import sys
import traceback
import ctypes

def importPluginModule(pluginPath, pluginName, excuteFilePath, version):
    if not os.path.isfile(pluginPath):
        print(f"not exist {pluginPath}")
        return None

    # moduleName = f"{pluginName}_r{version}.{excuteFilePath}"
    moduleName = f"{pluginName}_r{version}.client"
    print(f"import module {pluginPath} {moduleName}")
    module = None
    try:
        addPath2SysPath(pluginPath, pluginName)
        module = __import__(moduleName, globals(), locals(), ["eggs", "object"])
    except ImportError as e:
        # 文件存在又import不成功，可能是含有emoji表情字符的路径,拷贝到应用目录下
        src = os.path.normpath(pluginPath)
        dst = os.path.normpath(os.path.join(getAppPath(), os.path.basename(pluginPath)))
        if src != dst:
            print("copy {} -> {}".format(src, dst))
            try:
                copyFile(src, dst)
                addPath2SysPath(dst, pluginName)
                module = __import__(moduleName, globals(), locals(), ["eggs", "object"])
            except Exception as e:
                print(traceback.format_exc())
        else:
            print(traceback.format_exc())
    except Exception as e:
        print(traceback.format_exc())
    return module

def getAppPath():
    s = ctypes.create_unicode_buffer(300)
    t = ctypes.windll.kernel32.GetModuleFileNameW(None, ctypes.byref(s), 300)
    path = s.value
    path = path[:path.rfind(os.sep)]
    return path

def copyFile(srcfile, dstfile):
    try:
        # 支持带emoji表情的路径
        if os.path.isfile(srcfile) and not os.path.isfile(dstfile):
            fpath, fname = os.path.split(dstfile)  # 分离文件名和路径
            if not os.path.exists(fpath):
                os.makedirs(fpath)  # 创建路径
            input = open(srcfile, "rb")
            output = open(dstfile, "wb")
            while True:
                s = input.read(1024)
                if not s:
                    break
                output.write(s)
            input.close()
            output.close()
    except Exception as e:
        print(traceback.format_exc())

def addPath2SysPath(resPath, name):
    # 把name从unicode转为str，不然下面find会报错
    str_name = str(name)
    for item in [item for item in sys.path]:
        if item.find(str_name) != -1:
            sys.path.remove(item)

    sys.path.insert(0, resPath)
    print("addPath2SysPath {}".format(resPath))


if __name__ == "__main__":
    import sys, os
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    module = importPluginModule(r"F:\test\out_master\tcplinkprotocols-master-1662041606.res", "tcplinkprotocols", "client.main_widget", 1662041606)
    widget = module.create()
    widget.show()
    sys.exit(app.exec_())