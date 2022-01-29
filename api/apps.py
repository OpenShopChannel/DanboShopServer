from typing import Dict, Union

from flask import request

from models import AppsModel


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
        "display_name": app.meta_data.display_name,
        "downloads": 0,
        "extra_directories": [],
        "extracted": app.meta_data.file.extracted_size,
        "icon_url": url_for(app.meta_data.file_uuid, "icons"),
        "internal_name": app.slug,
        "long_description": app.meta_data.long_description,
        "package_type": "dol",
        "rating": "",
        "release_date": int(app.date_added.timestamp()),
        "short_description": app.meta_data.short_description,
        # "title_ids": {
        #     "sd_title": app.title_ids.sd_title,
        #     "nand_title": app.title_ids.nand_title,
        #     "forwarder_title": app.title_ids.forwarder_title,
        # },
        "updated": updated_date,
        "version": app.meta_data.display_version,
        "zip_size": app.meta_data.file.zip_size,
        "zip_url": url_for(app.meta_data.file_uuid, "zips"),
    }


def url_for(uuid_name: str, file_type: str) -> str:
    """Retrieves a URL. It's assumed that the caller has repo as a path parameter."""
    hostname = request.host
    repo = request.view_args["repo"]

    if file_type == "zips":
        extension = "zip"
    elif file_type == "icons":
        extension = "png"
    else:
        # This if statement should not be exhausted.
        extension = "???"

    return f"https://{hostname}/{repo}/{file_type}/{uuid_name}.{extension}"

