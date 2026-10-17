import os

import drafthorse

# pip builds the package from git in a temporary directory with a path of about
# 100 characters, Windows fails on paths with more than 260 characters
MAX_PATH_LENGTH = 80


def test_package_paths_are_short():
    root = os.path.dirname(os.path.dirname(drafthorse.__file__))
    package = os.path.dirname(drafthorse.__file__)
    too_long = []
    for dirpath, dirnames, filenames in os.walk(package):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for filename in filenames:
            path = os.path.relpath(os.path.join(dirpath, filename), root)
            if len(path) > MAX_PATH_LENGTH:
                too_long.append(path)
    assert too_long == []
