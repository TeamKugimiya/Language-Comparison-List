"""A simple script for auto update latest"""
import subprocess
import json
from pathlib import Path
import requests

def get_remote_branches(repo_url: str):
    """
    Using git ls-remote to get all branches
    """
    try:
        output = subprocess.check_output(['git', 'ls-remote', '--heads', repo_url]).decode("utf-8")
        lines = output.strip().split('\n')
        branches = [line.split('\t')[1].split('refs/heads/')[-1] for line in lines]
        return branches
    except subprocess.CalledProcessError as expect:
        print(f"Error running 'git ls-remote': {expect}")
        return []

def combiner(source_path: str, dest_path: str, template: int, version: str, output_file: Path):
    """
    Combine source and dest language file into one
    """

    with open(source_path, "r", encoding="utf8") as source_file, open(dest_path, "r", encoding="utf8") as dest_file, open(output_file, "w", encoding="utf8") as output_f:
        source_data = json.load(source_file)
        dest_data = json.load(dest_file)

        output_f.write(f"遊戲版本：{version}\n\n")

        match template:
            case 0:
                for key in source_data.keys():
                    output_f.write(f"翻譯鍵：<{key}>\n")
                    output_f.write(f"原始英文：{source_data[key]}\n")
                    output_f.write(f"繁體中文：{dest_data.get(key, '')}\n\n")
            case 1:
                for key in source_data.keys():
                    output_f.write(f"翻譯鍵：<{key}>\n")
                    output_f.write(f"繁體中文：{source_data[key]}\n")
                    output_f.write(f"簡體中文：{dest_data.get(key, '')}\n\n")

def download_language_file(version: str, path: str):
    """
    Download language files
    """
    urls = {
        f"https://raw.githubusercontent.com/InventivetalentDev/minecraft-assets/{version}/assets/minecraft/lang/en_us.json",
        f"https://raw.githubusercontent.com/InventivetalentDev/minecraft-assets/{version}/assets/minecraft/lang/zh_tw.json"
    }

    for url in urls:
        response = requests.get(url, timeout=6)

        if response.status_code == 200:
            filename = url.split("/")[-1]

            if not Path(path).exists():
                Path(path).mkdir()
            filepath = Path.cwd().joinpath(path, filename)

            with open(filepath, "wb") as file:
                file.write(response.content)

if __name__ == "__main__":
    # Get assets branches list
    github_repo_url = "https://github.com/InventivetalentDev/minecraft-assets"
    branches_list = get_remote_branches(github_repo_url)

    # Get latest game version
    mc_version_manifest = json.loads(requests.get("https://launchermeta.mojang.com/mc/game/version_manifest_v2.json", timeout=6).content)
    latest_game_version = mc_version_manifest["latest"]["release"]

    if latest_game_version in branches_list:
        download_language_file(latest_game_version, "latest")
        combiner(Path("latest/en_us.json"), Path("latest/zh_tw.json"), 0, latest_game_version, Path("latest/list.txt"))
        Path("latest/en_us.json").unlink()
        Path("latest/zh_tw.json").unlink()
    else:
        print("專案尚未包含最新版內容！")
