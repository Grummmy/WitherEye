from hashlib import sha512
import os, subprocess, requests, re, json, psutil, win32api
from platform import uname
from datetime import datetime
from rich.tree import Tree
from rich.console import Console
from rich.style import Style

console = Console()

logo = "WitherEye"
platform = uname()

def walk(path=".", n:int=-1):
    """
    Walks directories like os.walk(), but limits depth with `n`.
    
    Args:
        path (str): Starting path (default: ".").
        n (int): Max depth (-1 for unlimited, 1 to walk through `path` only).
    Yields:
        tuple: (root, dirs, files) for each directory. (same as original os.walk())
    """
    path = os.path.abspath(path)
    for root, dirs, files in os.walk(path):
        if n != -1 and root[len(path):].count(os.sep) > n:
            return
        yield root, dirs, files

def load_data(url:str) -> dict:
    """
    Gets data by url

    Args:
        url (str): url from which to request data.

    Returns:
        data (most likely dict): dict of data from the `url`.
    """
    data = requests.get(url)
    if data.status_code == 200:
        data = json.loads(data.text)
    else:
        print(f"\033[31mFailed to load data from GitHub. \033[1mError {data.status_code}\033[22m.\033[0m")
        print(f"\033[31mGitHub link: \033[34m\033[4m{url}\033[0m")
        exit()
    
    return data

data = load_data("https://raw.githubusercontent.com/Grummmy/WitherEye/refs/heads/main/data.json")
mc_launchers = re.compile(r"\b(" + "|".join(data["minecraft-launchers"]) + r")\b", re.IGNORECASE)
cheats = re.compile(r"\b(" + "|".join(data["cheats"]) + r")\b", re.IGNORECASE)
cheatsb = re.compile(rb"\b(" + b"|".join(word.encode() for word in data["cheats"]) + rb")\b", re.IGNORECASE)
modrinth = load_data("https://raw.githubusercontent.com/Grummmy/WitherEye/refs/heads/main/modrinthHash.json")
# curseforge = load_data("https://raw.githubusercontent.com/Grummmy/WitherEye/refs/heads/main/curseforgeHash.json")

class Mpath(str):
    """
    A class representing a Minecraft path with additional formatting.
    Inherits from str to represent the path as a string.
    """
    def __new__(cls, path: str):
        obj = super().__new__(cls, path)
        obj._path = path
        obj.f = mc_launchers.sub(r"\033[1m\g<0>\033[22m", path)
        return obj

def check_path(path:str|Mpath) -> Mpath | None:
    global mc_launchers

    if match:= mc_launchers.search(path):
        path = path[:path[match.end()-1:].find(os.sep)+match.end()-1]
        return Mpath(path)
    else:
        return None

zip = re.compile(r"\b\w+\.(zip|gz|rar|tar|7z|tgz)(\.\w+)*\b")
jar = re.compile(r"\b\w+\.(jar|litemod)(\.\w+)*\b")
def search(path="."):
    """
    Searches `path` for minecraft cheats

    Args:
        path (str): path to search. Defaults to current path (".")
    """
    global cheats, cheatsb, modrinth, jar, zip

    i = 0
    for root, _, files in walk(path):
        for file in files:
            if i == 10:
                i = 0
                input("Press \033[1menter\033[22m to continue ")
            # print(f"Checking {os.path.join(root, file)}")
            if cheats.search(file):
                i += 1
                print(f" - {root}{os.sep}{cheats.sub(r'\033[1m\g<0>\033[22m', file)}")

            if jar.search(file):
                sha512_hash = sha512()

                # print(f"Checking {os.path.join(root, file)}")
                with open(os.path.join(root, file), "rb") as f:
                    sha512_hash.update(f.read())

                if mod := modrinth.get(sha512_hash.hexdigest(), None):
                    print(f"   Original: {mod['name']}")
            elif zip.search(file):
                with open(os.path.join(root, file), "rb") as f:
                    if match := cheatsb.search(f.read()):
                        i += 1
                        print(f" + {match[0]} in {os.path.join(root, file)}")

def find_minecraft(p:bool=True) -> set[Mpath]:
    """
    Finds Minecraft directories based on a regex pattern.
    if mc_launchers.search(potential_minecraft_dir)
    
    Args:
        p (bool, optional): If True, prints found directories. Defaults to True.

    Returns:
        set[Mpath]: List of Minecraft paths.
    """
    global mc_launchers, platform, console

    generator = walk(os.environ.get("APPDATA"), 1) if platform.system[0] == "W" else walk(os.environ.get("HOME"), 3)
    minecraft = set()
    for root, dirs, files in generator:
        for dir in dirs:
            if mc_launchers.search(dir):
                minecraft.add(Mpath(os.path.join(root, dir)))
    
    if platform.system[0] == "W":
        for disk in psutil.disk_partitions():
            for root, dirs, files in walk(disk.mountpoint, 2):
                for dir in dirs:
                    if mc_launchers.search(dir):
                        minecraft.add(Mpath(os.path.join(root, dir)))
        for root, dirs, files in walk(os.path.expanduser("~"), 2):
            for dir in dirs:
                if mc_launchers.search(dir):
                    minecraft.add(Mpath(os.path.join(root, dir)))

    # ask user about Minecraft location, if Minecraft wasn't found
    while not minecraft or not os.path.exists(list(minecraft)[0]):
        try:
            minecraft = input('Minecraft was not found. Please enter a \033[1mfull valid path\033[0m, or exit(Ctrl+C) the program.\n - A folder-choosing window is \033[4mavailable only on Windows\033[0m, print \033[3mmenu\033[0m to call it.\n - If you want to pass several pathes, write each path separated by " | "(space, vertical bar, space).\n   └╴Example: first/minecraft/dir | second/minecraft/dir\n').strip()
            if minecraft == "menu":
                if platform.system[0] == "W":
                    minecraft = set()
                    while True:
                        proccess = subprocess.run('powershell -command "& {Add-Type -AssemblyName System.windows.forms; $f=New-Object System.Windows.Forms.FolderBrowserDialog; $f.ShowDialog(); $f.SelectedPath}"', capture_output=True, text=True)
                        if proccess.stdout[:2] == "OK":
                            path = proccess.stdout.strip().split("\n")[1]
                            minecraft.add(Mpath(path))
                        if more := input("Do you want to add one more path?[y/N] ").strip().lower():
                            if more == "" or more[0] not in ["y", "н"]:
                                break
                        else:
                            break
                else:
                    print("Sorry, your system isn't Windows(")

            if isinstance(minecraft, str):
                pathes = minecraft.split(" | ")
                minecraft = []
                for path in pathes:
                    if os.path.exists(path):
                        minecraft.add(Mpath(path))
            print("")
        except KeyboardInterrupt:
            if p:
                print("\nHave a good day, sir! And do not cheat!")
            exit()
    
    # print results found, if p
    if p:
        tree = Tree(f"Found \033[1m{len(minecraft)}\033[22m Minecraft folders:", guide_style=Style(bold=True))
        for i, path in enumerate(minecraft):
            tree.add(f"{i+1}. {path.f}")
        
        console.print(tree)
    
    return minecraft

proc_tree = Tree("Found Minecraft/Java processes:", guide_style=Style(bold=True))
mc_launchersj = re.compile(mc_launchers.pattern.replace(r")\b", r"|java)\b"), re.IGNORECASE)

def check_proc(exe:str, cwd:str, cmdline:list) -> bool:
    """
    Checks whether process arguments are related to Minecraft/cheats.
    
    Args:
        exe (str): path to the process' executable file.
        cwd (str): path to the process' working dir.
        cmdline (str): command line args of the process.

    Returns:
        bool: True if process args are related to Minecraft/cheats.
    """
    global mc_launchersj, cheats
    
    for p in [exe, cwd, " ".join(cmdline)]:
        if mc_launchersj.search(p):
            return True
        if cheats.search(p):
            return True

def check_processes(processes=psutil.process_iter(), branch:Tree|None=None, p:bool=True) -> tuple[set[psutil.Process], set[Mpath]]:
    """
    Checks running java/minecraft processes, prints info about them
    
    Args:
        processes (optional): list of processes to check. Defaults to all currently running processes.
        branch (Tree|Nont, optional): rich.Tree branch wheere to add child processes.
        p (bool, optional): If True, prints found directories. Defaults to True.

    Returns:
        list[psutil.Process] - List of Minecraft/Java processes.
        list[Mpath] - List of Minecraft paths.
    """
    global mc_launchersj, platform, proc_tree

    procs = set()
    pathes = set()
    for proc in processes:
        try:
            exe = proc.exe()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            exe = "\033[1mAccess Denied\033[22m"
        try:
            cwd = proc.cwd()
        except:
            cwd = "\033[1mAccess Denied\033[22m"
        try:
            cmdline = proc.cmdline()
        except:
            cmdline = "\033[1mAccess Denied\033[22m"

        if check_proc(exe, cwd, cmdline):
            procs.add(proc)

            if path := check_path(exe):
                pathes.add(path)

            if p:
                try:
                    fd = win32api.GetFileVersionInfo(exe, "\\StringFileInfo\\040904b0\\FileDescription")
                    file_description = " (" + (fd if fd else "\033[1mNo Descriptrion\033[22m") + ")" if platform.system[0] == "W" else ""
                except Exception as e:
                    file_description = ""
                    print(f"Error while getting the description of {exe}:\n{e}")

                if branch:
                    branch.add(f"{mc_launchersj.sub(rf"\033[1m\g<0>\033[22m", proc.name())}{file_description} ({proc.pid}) - {proc.status()}\n  ┣╸ Started on {datetime.fromtimestamp(proc.create_time())}\n  ┣╸ Executable: {exe}\n  ┣╸ Working dir: {cwd}\n  ┗╸ CMD arguments: {cmdline}")
                else:
                    branch = proc_tree.add(f"{mc_launchersj.sub(rf"\033[1m\g<0>\033[22m", proc.name())}{file_description} ({proc.pid}) - {proc.status()}\n  ┣╸ Started on {datetime.fromtimestamp(proc.create_time())}\n  ┣╸ Executable: {exe}\n  ┣╸ Working dir: {cwd}\n  ┗╸ CMD arguments: {cmdline}")
                if children := proc.children(True) and not branch: 
                    check_processes(children, branch)

    return procs, pathes

def main():
    summary = {}
    summary['minecraft'] = find_minecraft()
    proces = check_processes()
    console.print(proc_tree)
    summary['processes'] = proces[0]
    summary['minecraft'] = summary['minecraft'] | proces[1]
    
    print('-'*50)
    for path in summary['minecraft']:
        search(path)



if __name__ == "__main__":
    main()
