import os, subprocess, requests, re, json, psutil
from platform import uname

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
    Loads minecraft lunchers/cheat launchers and minecraft cheats/cheat mods from GitHub.
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
    not done, yet
    
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

    while not minecraft or not os.path.exists(minecraft[0][0]):
        try:
            minecraft = input("Minecraft was not found. Please enter a valid path, or exit(Ctrl+C) the program.\n").strip()
            if minecraft:
                minecraft = [(minecraft, os.path.dirname(minecraft) + os.sep + mc_launchers.sub(r"\033[1m\1\033[22m", os.path.basename(minecraft)))]
        except KeyboardInterrupt:
            if p:
                print("\nHave a good day, sir! And do not cheat!")
            exit()
    
    if p:
        print(f"Found \033[1m{len(minecraft)}\033[22m Minecraft folders:")
        for i, path in enumerate(minecraft):
            if i+1 != len(minecraft):
                print(f" ┣╸ {i+1}. {path[1]}")
                continue
            print(f" ┗╸ {i+1}. {path[1]}")
    
    return minecraft


# if match := re.search(r"java", os.environ["PATH"], re.I):
#     print(match.group())

# print("\n".join(path[1] for path in find_minecraft()))

def main():
    data = load_data()
    mc_launchers = re.compile(r"\b(" + "|".join(data["minecraft-launchers"]) + r")\b", re.IGNORECASE)
    find_minecraft(mc_launchers, platform.system)

if __name__ == "__main__":
    main()
