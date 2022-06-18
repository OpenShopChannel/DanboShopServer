from typing import Dict, Union

from flask import request

from models import AppsModel
from utils import FileTypes, storage_type_for_file


def app_to_dict(app: AppsModel) -> Dict[str, Union[str, int, list, dict]]:
    """Converts a queried AppsModel to a usable dictionary for the JSON API."""
    # Ensure we have a proper updated date.
    if app.date_updated:
        updated_date = int(app.date_updated.timestamp())
    else:
        updated_date = 0

    return {
        "category": app.category,
        "coder": app.author.display_name,
        "contributors": app.meta_data.contributors,
        "controllers": app.meta_data.controllers,
        "display_name": app.meta_data.display_name,
        "downloads": 0,
        "extra_directories": app.meta_data.file.extra_dirs,
        "extracted": app.meta_data.file.extracted_size,
        "hashes": {
            "md5": app.meta_data.file.md5,
            "sha256": app.meta_data.file.sha256,
        },
        "icon_url": url_for(app, FileTypes.ICON),
        "internal_name": app.slug,
        "long_description": app.meta_data.long_description,
        "package_type": app.meta_data.file.package_type,
        "rating": app.rating,
        "release_date": int(app.date_added.timestamp()),
        "short_description": app.meta_data.short_description,
        "title_ids": {
            "sd_title": app.title_ids.sd_title,
            "nand_title": app.title_ids.nand_title,
            "forwarder_title": app.title_ids.forwarder_title,
        },
        "updated": updated_date,
        "version": app.meta_data.display_version,
        "zip_size": app.meta_data.file.zip_size,
        "zip_url": url_for(app, FileTypes.ZIP),
    }


def url_for(app: AppsModel, file_type: FileTypes) -> str:
    """Retrieves a URL for the given file type."""
    extension = file_type.value
    storage_dir = storage_type_for_file(file_type).value

    hostname = request.host
    repo = app.repo.id
    slug = app.slug
    return f"https://{hostname}/{repo}/{storage_dir}/{slug}.{extension}"

