import os, subprocess
from platform import uname
from rich import print

"""
1. find minecraft
2. Find Java, check version(s) and pathes
3. find all java/javaw processes
"""

logo = "WitherEye"
platform = uname()
os.original_walk = os.walk

def walk(path=".", n:int=-1):
    """
    Walks directories like os.walk(), but limits depth with 'n'.
    
    Args:
        path (str): Starting path (default: ".").
        n (int): Max depth (-1 for unlimited).
    
    Yields:
        tuple: (root, dirs, files) for each directory.
    """
    path = os.path.abspath(path)
    for root, dirs, files in os.original_walk(path):
        if root[len(path):].count(os.sep) > n:
            return
        yield root, dirs, files

os.walk = walk

def search(path=".", n=2):
    """
    not done, yet
    
    should check directory for targeted words
    """
    if n == 0:
        return

    for file in os.walk(path):
        pass

def find_minecraft():
    """
    Finds Minecraft, hopefully, on all systems!
    if it's present at all.
    """
    if platform.system[0] == "W":
        path = {
            "m": os.path.expandvars("%appdata%\\.minecraft"),
            "t": os.path.expandvars("%appdata%\\.tlauncher")
        }
        minecraft = ""

        if os.path.exists(path["m"]):
            minecraft = os.path.abspath(path["m"])
        elif os.path.exists(path["t"]):
            # if there are folders "Legacy" and "launcher", to ensure that this is Tl Legacy, and not Tlauncher.
            dirs = {entry.name for entry in os.scandir(path["t"]) if entry.is_dir()}
            if {"legacy", "logs"}.issubset(dirs):
                minecraft = os.path.abspath(path["t"])

        while (not os.path.exists(minecraft)) or (not minecraft):
            proccess = subprocess.run('powershell -command "& {Add-Type -AssemblyName System.windows.forms; $f=New-Object System.Windows.Forms.FolderBrowserDialog; $f.ShowDialog(); $f.SelectedPath}"', capture_output=True, text=True)
            if proccess.stdout[:2] == "OK":
                minecraft = proccess.stdout.strip().split("\n")[1]
            else:
                minecraft = input("Where is your main Minecraft folder?\n")
        
        return minecraft

    elif platform.system[0] == "L":
        pass

print(find_minecraft())