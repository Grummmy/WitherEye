import os, subprocess, requests, re, json
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
url = "https://raw.githubusercontent.com/Grummmy/WitherEye/refs/heads/main/data.json"
data = requests.get(url)
if data.status_code == 200:
    data = json.loads(data.text)
else:
    print(f"[red]Failed to load data from GitHub. [bold]Error {data.status_code}[/bold].[/red]")
    print(f"[red]GitHub link:[/red] {url}")
    exit()

mc_launchers = re.compile(r"\b(" + "|".join(data["minecraft-launchers"]) + r")\b", re.IGNORECASE)


def walk(path=".", n:int=-1):
    """
    Walks directories like os.walk(), but limits depth with `n`.
    
    Args:
        path (str): Starting path (default: ".").
        n (int): Max depth (-1 for unlimited, 0 to walk through `path` only).
    Yields:
        tuple: (root, dirs, files) for each directory.
    """
    path = os.path.abspath(path)
    for root, dirs, files in os.original_walk(path):
        if n != -1 and root[len(path):].count(os.sep) > n:
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
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    minecraft = []
    for root, dirs, files in os.walk(appdata, 1):
        for dir in dirs:
            if mc_launchers.search(dir):
                minecraft.append((os.path.join(root, dir), root + os.sep + mc_launchers.sub(r"\033[1m\1\033[0m", dir)))
    
    while not minecraft or not os.path.exists(minecraft[0][0]):
        try:
            minecraft = input("Minecraft was not found. Please enter the path, or exit(Ctrl+C) the program.\n").strip()
            
        except KeyboardInterrupt:
            print("Have a good day, sir! And do not cheat!")
            exit()

# if match := re.search(r"java", os.environ["PATH"], re.I):
#     print(match.group())

print("\n".join(path[0] for path in find_minecraft()))
