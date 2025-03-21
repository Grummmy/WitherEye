import os, subprocess, requests, re, json, psutil
from platform import uname
from datetime import datetime

"""
1. find minecraft
2. find Java, check version(s) and pathes
3. find all java/javaw processes
"""

logo = "WitherEye"
platform = uname()
os.original_walk = os.walk

def walk(path=".", n:int=-1):
    """
    Walks directories like os.walk(), but limits depth with `n`.
    
    Args:
        path (str): Starting path (default: ".").
        n (int): Max depth (-1 for unlimited, 1 to walk through `path` only).
    Yields:
        tuple: (root, dirs, files) for each directory.
    """
    path = os.path.abspath(path)
    for root, dirs, files in os.original_walk(path):
        if n != -1 and root[len(path):].count(os.sep) > n:
            return
        yield root, dirs, files

os.walk = walk


def load_data() -> dict:
    """
    Loads minecraft lunchers/cheat-clients and minecraft cheats/cheat mods from GitHub.
    """
    url = "https://raw.githubusercontent.com/Grummmy/WitherEye/refs/heads/main/data.json"
    data = requests.get(url)
    if data.status_code == 200:
        data = json.loads(data.text)
    else:
        print(f"\033[31mFailed to load data from GitHub. \033[1mError {data.status_code}\033[22m.\033[0m")
        print(f"\033[31mGitHub link: \033[34m\033[4m{url}\033[0m")
        exit()
    
    return data

def search(path=".", n=2):
    """
    NOT DONE, YET
    
    should check directory for targeted words
    """
    if n == 0:
        return

    for file in os.walk(path):
        pass

def find_minecraft(mc_launchers:re.Pattern, system:str, p:bool=True) -> list[tuple[str, str]]:
    """
    Finds Minecraft directories based on a regex pattern.
    if mc_launchers.search(potential_minecraft_dir)

        mc_launchers (re.Pattern): Compiled regex pattern to match directories.
        system (str): OS identifier ('Windows' or 'Linux').
        p (bool, optional): If True, prints found directories. Defaults to True.

    Returns:
        list[tuple[str, str]]: List of tuples with raw and highlighted paths.
    """
    generator = os.walk(os.environ.get("APPDATA"), 1) if platform.system[0] == "W" else os.walk(os.environ.get("HOME"), 3)
    minecraft = []
    for root, dirs, files in generator:
        for dir in dirs:
            if mc_launchers.search(dir):
                minecraft.append((os.path.join(root, dir), root + os.sep + mc_launchers.sub(r"\033[1m\1\033[22m", dir)))
    
    if system[0] == "W":
        for disk in psutil.disk_partitions():
            for root, dirs, files in os.walk(disk.mountpoint, 2):
                for dir in dirs:
                    if mc_launchers.search(dir):
                        minecraft.append((os.path.join(root, dir), root + os.sep + mc_launchers.sub(r"\033[1m\1\033[22m", dir)))
        for root, dirs, files in os.walk(os.path.expanduser("~"), 2):
            for dir in dirs:
                if mc_launchers.search(dir):
                    minecraft.append((os.path.join(root, dir), root + os.sep + mc_launchers.sub(r"\033[1m\1\033[22m", dir)))

    # ask user about Minecraft location, if Minecraft wasn't found
    while not minecraft or not os.path.exists(minecraft[0][0]):
        try:
            minecraft = input('Minecraft was not found. Please enter a \033[1mvalid path\033[0m, or exit(Ctrl+C) the program.\n - A folder-choosing window is \033[4mavailable only on Windows\033[0m, print \033[3mmenu\033[0m to call it.\n - If you want to pass several pathes, write each path separated by " | "(space, vertical bar, space).\n   └╴Example: first/minecraft/dir | second/minecraft/dir\n').strip()
            if minecraft == "menu":
                if system[0] == "W":
                    minecraft = []
                    while True:
                        proccess = subprocess.run('powershell -command "& {Add-Type -AssemblyName System.windows.forms; $f=New-Object System.Windows.Forms.FolderBrowserDialog; $f.ShowDialog(); $f.SelectedPath}"', capture_output=True, text=True)
                        if proccess.stdout[:2] == "OK":
                            path += proccess.stdout.strip().split("\n")[1]
                            minecraft.appned((path, os.path.dirname(path) + os.sep + mc_launchers.sub(r"\033[1m\1\033[22m", os.path.basename(path))))
                        if more := input("Do you want to add one more path?[y/N] ").strip().lower() or more == "" or more[0] not in ["y", "н"]:
                            break
                else:
                    print("Sorry, your system isn't Windows(")

            if isinstance(minecraft, str):
                pathes = minecraft.split(" | ")
                minecraft = []
                for path in pathes:
                    if os.path.exists(path):
                        minecraft.appned((path, os.path.dirname(path) + os.sep + mc_launchers.sub(r"\033[1m\1\033[22m", os.path.basename(path))))
            print("")
        except KeyboardInterrupt:
            if p:
                print("\nHave a good day, sir! And do not cheat!")
            exit()
    
    # print results found, if p
    if p:
        print(f"Found \033[1m{len(minecraft)}\033[22m Minecraft folders:")
        for i, path in enumerate(minecraft):
            if i+1 != len(minecraft):
                print(f" ┣╸ {i+1}. {path[1]}")
                continue
            print(f" ┗╸ {i+1}. {path[1]}")
    
    return minecraft

def check_processes(pattern:re.Pattern, p:bool=True) -> list[psutil.Process]:
    """
    NOT DONE, YET
    
    Checks running java/minecraft processes, prints info about them
    
    Returns:
        list[psutil.Process] - found processes list
    """
    procs = []
    for proc in psutil.process_iter(['name', 'pid', 'status', 'create_time','exe', 'cwd', 'cmdline']):
        if pattern.search(proc.info['name']) or pattern.search(proc.info['exe'] if proc.info['exe'] else ""):
            proc = proc.info
            procs.append(psutil.Process(proc['pid']))
            if p:
                print(f"{pattern.sub(rf"\033[1m\g<0>\033[22m", proc['name'])}\n ┣╸ {proc['status']} ({proc['pid']})\n ┣╸ Started on {datetime.fromtimestamp(proc['create_time'])}\n ┣╸ Executable: {proc['exe']}\n ┣╸ Working dir: {proc['cwd']}\n ┗╸ CLI args: {proc["cmdline"]}")

    return procs

def main():
    data = load_data()
    mc_launchers = re.compile(r"\b(" + "|".join(data["minecraft-launchers"]) + r")\b", re.IGNORECASE)
    find_minecraft(mc_launchers, platform.system)
    check_processes(re.compile(mc_launchers.pattern.replace(r")\b", r"|java)\b"), re.IGNORECASE))

if __name__ == "__main__":
    main()
