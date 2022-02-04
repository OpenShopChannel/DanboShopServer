import json
import os
import tempfile

import requests
from packaging import version

from models import AppsModel
import re


def check_for_update(slug):
    manifest_path = "updater/manifests/" + slug + ".json"
    if os.path.isfile(manifest_path):
        app = AppsModel.query.filter_by(slug=slug).first()

        # Read manifest
        manifest = json.load(open(manifest_path))

        # Check if the version is newer
        if manifest["Source"].lower() == "github":
            # Get json from url https://api.github.com/repos/DacoTaco/priiloader/releases/latest
            url = "https://api.github.com/repos/" + manifest["Repository"] + "/releases/latest"
            latest_release = requests.get(url).json()
            if manifest["VersionSource"] == "tag_name":
                latest_version = re.search(manifest["VersionRegex"], latest_release["tag_name"]).group(0)
                if version.parse(latest_version) > version.parse(app.meta_data.display_version):
                    return True
    return False


def update_app(slug):
    manifest_path = "updater/manifests/" + slug + ".json"
    if os.path.isfile(manifest_path):
        # Read manifest
        manifest = json.load(open(manifest_path))

        if manifest["Source"].lower() == "github":
            url = "https://api.github.com/repos/" + manifest["Repository"] + "/releases/latest"
            latest_release = requests.get(url).json()

            # Iterate files in GitHub release
            for asset in latest_release["assets"]:
                # Match against zip file regex from manifest
                if re.search(manifest["ZipRegex"], asset["name"]):
                    url = asset["browser_download_url"]
                    # create temp dir and download file
                    with tempfile.TemporaryDirectory() as tmpdir:
                        filename = os.path.join(tmpdir, asset["name"])
                        with open(filename, "wb") as f:
                            f.write(requests.get(url).content)

                            # todo - scrape the zip file for the app's folder location

                        return True
            return False
