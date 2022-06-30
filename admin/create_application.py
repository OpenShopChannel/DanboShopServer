import os
import shutil
import uuid
import requests
import zipfile
from datetime import date
from typing import Dict

from models import AuthorModel, db, MetadataModel, FileStatsModel, AppsModel, TitleIDsModel
from titles import get_title_id, TitleType
from utils import file_path, FileTypes, md5sum_file, sha256sum_file, storage_path, StorageTypes


def import_for(repo: str):
    """Queries the existing API for metadata, and inserts entries accordingly into the DB.

    This function exists only to assist with migration from the previous API.
    It serves as an example of app addition."""
    req = requests.get(f"https://api.oscwii.org/v2/{repo}/packages")
    apps: [Dict] = req.json()

    # Iterate through all apps, adding them accordingly.
    for app in apps:
        # Obtain the app's author.
        author = lookup_author(app["coder"])

        # This will be our app's UUID.
        generated_uuid = process_files(app)

        # Prepare to insert our application.
        date_added = date.fromtimestamp(app["release_date"])
        if app["updated"] != 0:
            date_updated = date.fromtimestamp(app["updated"])
        else:
            date_updated = date_added

        app_model = AppsModel(
            slug=app["internal_name"],
            repo_id=repo,
            date_added=date_added,
            date_updated=date_updated,
            category=app["category"],
            author_id=author.id,
        )

        db.session.add(app_model)
        db.session.commit()

        # Add title metadata.
        metadata = MetadataModel(
            application_id=app_model.id,
            display_name=app["display_name"],
            display_version=app["version"],
            short_description=app["short_description"],
            long_description=app["long_description"],
            contributors=app["contributors"],
            controllers=app["controllers"],
            file_uuid=generated_uuid
        )
        db.session.add(metadata)

        # Add title IDs.
        title_ids = TitleIDsModel(
            application_id=app_model.id,
            sd_title=get_title_id(TitleType.SD, app_model.id),
            nand_title=get_title_id(TitleType.NAND, app_model.id),
            forwarder_title=get_title_id(TitleType.FORWARDER, app_model.id),
        )
        db.session.add(title_ids)
        db.session.commit()


def process_files(app: Dict) -> str:
    """Scrapes file information, inserting accordingly."""

    # This will be our app's UUID.
    file_uuid = str(uuid.uuid4())

    # Ensure it is unused.
    if FileStatsModel.query.where(FileStatsModel.id == file_uuid).all():
        # Call this function again, looping until we have an unused UUID.
        return process_files(app)

    # Download our zip and icon.
    download_icon(app["icon_url"], file_uuid)
    zip_path = download_zip(app["zip_url"], file_uuid)

    # Obtain hashes of our downloaded zip.
    md5 = md5sum_file(zip_path).hex()
    sha256 = sha256sum_file(zip_path).hex()

    # Extract the zip.
    extract_path = storage_path(StorageTypes.UNZIPPED, file_uuid)
    with zipfile.ZipFile(zip_path, "r") as extract:
        extract.extractall(extract_path)

    # Determine size information.
    zip_size = os.path.getsize(zip_path)

    # Loop through all files in the directory.
    # We consider extra directories those who are not apps/slug.
    slug = app["internal_name"]
    extracted_size = 0
    extra_dirs = []

    apps_dir = os.path.abspath(os.path.join(extract_path, "apps"))
    slug_dir = os.path.abspath(os.path.join(extract_path, "apps", slug))

    for current_path, folders, files in os.walk(extract_path):
        for folder in folders:
            current_folder = os.path.join(current_path, folder)
            abs_path = os.path.abspath(current_folder)

            # Check if we are in the slug directory.
            if abs_path == apps_dir or abs_path == slug_dir:
                continue

            # Trim the leading extract dir for our extra dir's path.
            extra_path = abs_path.replace(extract_path, "")
            extra_dirs.append(extra_path)

        for file in files:
            # Add this file to the total extracted size.
            current_file = os.path.join(current_path, file)
            file_size = os.path.getsize(current_file)
            extracted_size += file_size

    if os.path.exists(os.path.join(slug_dir, "boot.dol")):
        package_type = "dol"
        package_size = os.path.getsize(os.path.join(slug_dir, "boot.dol"))
    elif os.path.exists(os.path.join(slug_dir, "boot.elf")):
        package_type = "elf"
        package_size = os.path.getsize(os.path.join(slug_dir, "boot.elf"))
    elif os.path.join(slug_dir, "theme.zip"):
        package_type = "thm"
        package_size = os.path.getsize(os.path.join(slug_dir, "theme.zip"))
    else:
        print("Invalid package type!")
        raise ValueError

    # Copy the icon and meta files.
    icon_size = os.path.getsize(os.path.join(slug_dir, "icon.png"))
    shutil.copy(os.path.join(slug_dir, "icon.png"), file_path(file_uuid, FileTypes.ICON))
    shutil.copy(os.path.join(slug_dir, "meta.xml"), file_path(file_uuid, FileTypes.META))

    # Generate a file model after our obtained data.
    file_stats = FileStatsModel(
        id=file_uuid,
        extracted_size=extracted_size,
        zip_size=zip_size,
        icon_size=icon_size,
        extra_dirs=extra_dirs,
        md5=md5,
        sha256=sha256,
        package_type=package_type,
        package_size=package_size
    )

    # Insert.
    db.session.add(file_stats)
    db.session.commit()

    return file_uuid


def lookup_author(name: str) -> AuthorModel:
    """Looks up an author in the database.

    If an author is already registered, their record is returned.
    If not, the author is added."""
    author: [AuthorModel] = AuthorModel.query\
        .where(AuthorModel.display_name == name)\
        .limit(1)\
        .all()

    if author:
        return author[0]
    else:
        # We need to create an author by this name.
        author = AuthorModel(display_name=name)
        db.session.add(author)
        db.session.commit()
        return author


def download_zip(file_url: str, file_uuid: str) -> str:
    """Downloads the given zip file, returning its path."""
    return download_file(file_url, file_uuid, FileTypes.ZIP)


def download_icon(file_url: str, file_uuid: str) -> str:
    """Downloads the given icon, returning its path."""
    return download_file(file_url, file_uuid, FileTypes.ICON)


def download_file(file_url: str, file_uuid: str, file_type: FileTypes) -> str:
    """Downloads the given URL to its appropriate path, returning the path.

    Parts of this function are adopted from https://stackoverflow.com/a/39217788."""
    download_path = file_path(file_uuid, file_type)

    with requests.get(file_url, stream=True) as contents:
        with open(download_path, 'wb') as file:
            shutil.copyfileobj(contents.raw, file)

    return download_path
