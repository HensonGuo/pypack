import re
import os

pattern_text_list_package = [
    "import {package_name}\.",
    "import {package_name}\W",
    "from {package_name} import",
    "from {package_name}\.",
]

origin_text_list_package = [
    "import {package_name}",
    "import {package_name}",
    "from {package_name} import",
    "from {package_name}.",
]

replace_text_list_package = [
    "import {res_name}.{package_name}",
    "from {res_name} import {package_name}",
    "from {res_name}.{package_name} import",
    "from {res_name}.{package_name}.",
]


def initPatternList(package_name, res_name):
    pattern_text_list = [i.format(package_name=package_name) for i in pattern_text_list_package]
    pattern_list = [re.compile(i) for i in pattern_text_list]
    origin_text_list = [i.format(package_name=package_name, ) for i in origin_text_list_package]
    replace_text_list = [i.format(package_name=package_name, res_name=res_name) for i in replace_text_list_package]
    return pattern_list, origin_text_list, replace_text_list


def changeImports(temp_dir, res_name, root_packages):
    src_dir = "{}{}/".format(temp_dir, res_name)

    root_packages_2_patterns = {}
    for root_package_name in root_packages:
        pattern_list, origin_text_list, replace_text_list = initPatternList(root_package_name, res_name)
        root_packages_2_patterns[root_package_name] = {
            "pattern_list": pattern_list,
            "origin_text_list":origin_text_list,
            "replace_text_list":replace_text_list
        }

    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if not file.endswith("py"):
                continue
            filepath = os.path.join(root, file)
            f = open(filepath, "r+", encoding="utf-8")
            new_content = []
            for line in f.readlines():
                find = False
                new_line = line
                for package_name in root_packages_2_patterns:
                    pattern = root_packages_2_patterns[package_name]
                    pattern_list = pattern["pattern_list"]
                    origin_text_list = pattern["origin_text_list"]
                    replace_text_list = pattern["replace_text_list"]

                    for pattern, origin_text, replace_text in zip(pattern_list, origin_text_list, replace_text_list):
                        if pattern.search(new_line):
                            new_text = replace_text.format(res_name=res_name, package_name=package_name)
                            new_line = new_line.replace(origin_text, new_text)
                            find = True
                            break
                    if find:
                        break
                new_content.append(new_line if find else line)
            f.seek(0)
            f.truncate()
            f.write("".join(new_content))
            f.close()