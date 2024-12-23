"""A simple script for auto update latest"""
import os
import sys
import json
import requests
import subprocess
from pathlib import Path

# Constants
MC_VERSION_MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest_v2.json"
GITHUB_REPO_URL = "https://github.com/InventivetalentDev/minecraft-assets"
GITHUB_REPO_URL_RAW = "https://raw.githubusercontent.com/InventivetalentDev/minecraft-assets/"
LANG_DIR = "assets/minecraft/lang"
LANG_FILES = ["en_us.json", "zh_tw.json"]

def get_remote_branches(repo_url: str):
    """
    Get GitHub branch list and return json.
    """
    try:
        output = subprocess.check_output(['git', 'ls-remote', '--heads', repo_url]).decode("utf-8")
        lines = output.strip().split('\n')
        branches = [line.split('\t')[1].split('refs/heads/')[-1] for line in lines]
        return branches
    except subprocess.CalledProcessError as ex:
        print(f"Error running 'git ls-remote': {ex}")
        return []

def fetch_language_file(repo_url: str, version: str, lang_file: str):
    """
    Fetch language file and return json dict
    """
    url = f"{repo_url}/{version}/{LANG_DIR}/{lang_file}"
    try:
        response = requests.get(url, timeout=6)
        response.raise_for_status()
        return json.loads(response.content)
    except requests.exceptions.RequestException as ex:
        print(f"Error fetching language file '{lang_file}': {ex}")
        return {}

def combine_and_write_language_files(source_data: dict, dest_data: dict, template: int, version: str, directory_path: Path, output_name: str):
    """
    Using source data and dest data json dict, combine together and output a file
    """

    if not directory_path.exists():
        Path.mkdir(directory_path)

    with open(directory_path.joinpath(f"{output_name}"), "w", encoding="utf8") as output_f:
        output_f.write(f"遊戲版本：{version}\n\n")
        for key in source_data.keys():
            output_f.write(f"翻譯鍵：<{key}>\n")
            if template == 0:
                output_f.write(f"原始英文：{source_data[key]}\n")
                output_f.write(f"繁體中文：{dest_data.get(key, '')}\n\n")
            elif template == 1:
                output_f.write(f"翻譯鍵：<{key}>\n")
                output_f.write(f"繁體中文：{source_data[key]}\n")
                output_f.write(f"簡體中文：{dest_data.get(key, '')}\n\n")

def github_output(output_name: str, output_content: str):
    """
    Simple output step content
    """

    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf8") as env:
        env.write(f"{output_name}={output_content}")

if __name__ == "__main__":
    branches_list = get_remote_branches(GITHUB_REPO_URL)

    mc_version_manifest = json.loads(requests.get(MC_VERSION_MANIFEST_URL, timeout=6).content)
    latest_game_version = mc_version_manifest["latest"]["release"]

    if len(sys.argv) >= 2:
        version = sys.argv[1]
        if sys.argv[1] in branches_list:
            lang_source = fetch_language_file(GITHUB_REPO_URL_RAW, version, LANG_FILES[0])
            lang_dest = fetch_language_file(GITHUB_REPO_URL_RAW, version, LANG_FILES[1])
            dir_path = Path(version)
            output_file_name = "list.txt"
            combine_and_write_language_files(lang_source, lang_dest, 0, version, dir_path, output_file_name)
        else:
            print("錯誤遊戲版本！")
        github_output("mc_version", sys.argv[1])
    else:
        if latest_game_version in branches_list:
            lang_source = fetch_language_file(GITHUB_REPO_URL_RAW, latest_game_version, LANG_FILES[0])
            lang_dest = fetch_language_file(GITHUB_REPO_URL_RAW, latest_game_version, LANG_FILES[1])
            dir_path = Path(latest_game_version)
            output_file_name = "list.txt"
            combine_and_write_language_files(lang_source, lang_dest, 0, latest_game_version, dir_path, output_file_name)
        else:
            print("專案尚未包含最新版內容！")
        github_output("mc_version", latest_game_version)
