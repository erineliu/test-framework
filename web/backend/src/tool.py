import os

def buildPath(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path
