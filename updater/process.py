import json
import logging
import os
import shutil
import tempfile
import zipfile
import glob
import pathlib
import config

import requests
from packaging import version

from models import AppsModel, db
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
            latest_release = requests.get(url, auth=('user', config.GITHUB_ACCESS_TOKEN)).json()
            if manifest["VersionSource"] == "tag_name":
                latest_version = re.search(manifest["VersionRegex"], latest_release["tag_name"]).group(0)
                if version.parse(latest_version) > version.parse(app.meta_data.display_version):
                    return True
    return False


def update_app(slug):
    manifest_path = "updater/manifests/" + slug + ".json"
    if os.path.isfile(manifest_path):
        app = AppsModel.query.filter_by(slug=slug).first()
        # Read manifest
        manifest = json.load(open(manifest_path))

        if manifest["Source"].lower() == "github":
            url = "https://api.github.com/repos/" + manifest["Repository"] + "/releases/latest"
            latest_release = requests.get(url, auth=('user', config.GITHUB_ACCESS_TOKEN)).json()
        else:
            logging.warning('Failed to update application ' + slug
                            + ", Unsupported source: " + manifest["Source"])
            return False

        # Iterate files in GitHub release
        for asset in latest_release["assets"]:
            # Match against zip file regex from manifest
            if re.search(manifest["ZipRegex"], asset["name"]):
                url = asset["browser_download_url"]

                # create temp dir and download file
                # todo move this process to a common function, shared with manual updating
                with tempfile.TemporaryDirectory() as tmpdir:
                    filename = os.path.join(tmpdir, asset["name"])

                    with open(filename, "wb") as f:
                        f.write(requests.get(url, auth=('user', config.GITHUB_ACCESS_TOKEN)).content)

                    # Extract zip file
                    with zipfile.ZipFile(filename, "r") as zip_ref:
                        zip_ref.extractall(tmpdir)

                    # Delete zip file
                    os.remove(filename)

                    # Run post fetch tasks
                    if "PostFetch" in manifest:
                        if "delete" in manifest["PostFetch"]:
                            for file in manifest["PostFetch"]["delete"]:
                                # check if is directory
                                if os.path.isdir(os.path.join(tmpdir, file)):
                                    shutil.rmtree(os.path.join(tmpdir, file))
                                else:
                                    os.remove(os.path.join(tmpdir, file))

                    # Find the 3 required files and verify they are all in the same directory.
                    # Note that we are ignoring the possibility that there are multiple dols and xmls,
                    # those will fail and return False. Should think out a solution for them later.
                    dol_path = glob.glob(tmpdir + '/**/apps/**/boot.dol', recursive=True)[0]
                    meta_path = glob.glob(tmpdir + '/**/apps/**/meta.xml', recursive=True)[0]
                    icon_path = glob.glob(tmpdir + '/**/apps/**/icon.png', recursive=True)[0]

                    if os.path.dirname(dol_path) == os.path.dirname(meta_path) == os.path.dirname(icon_path):
                        # Get path to copy from and pack zip
                        path = pathlib.Path(os.path.dirname(dol_path)).parent.parent

                        # Create zip file from directory
                        with zipfile.ZipFile("temp.zip", "w", zipfile.ZIP_DEFLATED) as zip_ref:
                            for file in path.rglob("*"):
                                relative_path = file.relative_to(path)
                                zip_ref.write(file, arcname=relative_path)

                        # Start updating app in storage
                        uuid = app.meta_data.file_uuid

                        # First off, delete the existing files
                        os.remove(f"{config.FILE_STORAGE_PATH}/zipped/{uuid}.zip")
                        shutil.rmtree(f"{config.FILE_STORAGE_PATH}/unzipped/{uuid}")
                        os.remove(f"{config.FILE_STORAGE_PATH}/metas/{uuid}.xml")
                        os.remove(f"{config.FILE_STORAGE_PATH}/icons/{uuid}.png")

                        # Now, copy the new files
                        shutil.copy(icon_path, f"{config.FILE_STORAGE_PATH}/icons/{uuid}.png")
                        shutil.copy(meta_path, f"{config.FILE_STORAGE_PATH}/metas/{uuid}.xml")
                        shutil.copy("temp.zip", f"{config.FILE_STORAGE_PATH}/zipped/{uuid}.zip")
                        shutil.unpack_archive(f"{config.FILE_STORAGE_PATH}/zipped/{uuid}.zip",
                                              f"{config.FILE_STORAGE_PATH}/unzipped/{uuid}")

                        os.remove("temp.zip")

                        # Update the app in the database
                        # important: todo update ALL information, and use version specified in meta.xml
                        app.meta_data.display_version = latest_release["tag_name"]

                        # Up internal version number
                        app.version += 1

                        # Commit to database
                        db.session.commit()

                        # Log
                        logging.info("Updated app " + slug + " to version " + latest_release["tag_name"])
                        return True
                    else:
                        logging.warning('Failed to update application '
                                        + slug + ", The 3 required files are not in the same directory")
                        return False
        return False
