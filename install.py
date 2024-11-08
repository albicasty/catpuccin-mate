#!/usr/bin/env python3
import json
import argparse
import subprocess
from typing import Union
import ast

arg_parser = argparse.ArgumentParser(prog='Catppuccin Theme - Mate-Terminal Installation',
                                     description='Installs the catppuccin theme for mate-terminal')
arg_parser.add_argument('-l', '--local', action='store')
args = arg_parser.parse_args()

if args.local is None:
    try:
        palette_repo = "https://raw.githubusercontent.com/catppuccin/palette"
        commit_sha = "407fb8c7f0ddee55bd10999c9b7e78f8fec256c5"
        res = subprocess.check_output(["curl", f"{palette_repo}/{commit_sha}/palette.json"]).decode("utf-8")
        palette = json.loads(res)
    except Exception as e:
        print(f"Error fetching the palette: {e}")
        exit(1)
else:
    try:
        with open(args.local) as local_palette:
            palette = json.load(local_palette)
    except Exception as e:
        print(f"Error fetching the palette: {e}")
        exit(1)

dconf_path_base = "/org/mate/terminal/profiles/"
uuids = {
    "mocha": "95894cfd-82f7-430d-af6e-84d168bc34f5",
    "macchiato": "5083e06b-024e-46be-9cd2-892b814f1fc8",
    "frappe": "71a9971e-e829-43a9-9b2f-4565c855d664",
    "latte": "de8a9081-8352-4ce4-9519-5de655ad9361",
}


def dconf_get(key: str):
    return ast.literal_eval(subprocess.check_output(["dconf", "read", key]).decode("utf-8").strip())


def dconf_set(key: str, value: Union[dict, list, str, bool]) -> None:
    if type(value) in [dict, list]:
        value = json.dumps(value).replace('"', "'")
    elif type(value) == str:
        value = f"'{value}'"
    elif type(value) == bool:
        value = str(value).lower()

    print(f"Setting {key} to {value}")
    subprocess.check_output(["dconf", "write", key, value])


# handle the case where there are no profiles
try:
    profiles = dconf_get("/org/mate/terminal/global/profile-list")
except:
    profiles = []

for flavour, colours in palette.items():
    uuid = uuids[flavour]
    dconf_set(f"{dconf_path_base}{uuid}/visible-name", f"Catppuccin {flavour.capitalize()}")
    dconf_set(f"{dconf_path_base}{uuid}/background-color", colours["base"]["hex"])
    dconf_set(f"{dconf_path_base}{uuid}/foreground-color", colours["text"]["hex"])
    dconf_set(f"{dconf_path_base}{uuid}/highlight-colors-set", True)
    dconf_set(f"{dconf_path_base}{uuid}/highlight-background-color", colours["rosewater"]["hex"])
    dconf_set(f"{dconf_path_base}{uuid}/highlight-foreground-color", colours["surface2"]["hex"])
    dconf_set(f"{dconf_path_base}{uuid}/cursor-colors-set", True)
    dconf_set(f"{dconf_path_base}{uuid}/cursor-background-color", colours["rosewater"]["hex"])
    dconf_set(f"{dconf_path_base}{uuid}/cursor-foreground-color", colours["base"]["hex"])

    isLatte = flavour == "latte"
    colors = [
        isLatte and colours["subtext1"] or colours["surface1"],
        colours["red"],
        colours["green"],
        colours["yellow"],
        colours["blue"],
        colours["pink"],
        colours["teal"],
        isLatte and colours["surface2"] or colours["subtext1"],
        isLatte and colours["subtext0"] or colours["surface2"],
        colours["red"],
        colours["green"],
        colours["yellow"],
        colours["blue"],
        colours["pink"],
        colours["teal"],
        isLatte and colours["surface1"] or colours["subtext0"],
    ]
    dconf_set(f"{dconf_path_base}{uuid}/use-theme-colors", False)
    # get only the hex key from each entry in colors
    dconf_set(f"{dconf_path_base}{uuid}/palette", [color["hex"] for color in colors])

    if uuid not in profiles:
        print(profiles)
        profiles.append(uuid)

dconf_set("/org/mate/terminal/global/profile-list", profiles)
print("All profiles installed.")
