from typing import Dict, Union

from models import AppsModel


def app_to_dict(app: AppsModel) -> Dict[str, Union[str, int, list, dict]]:
    """Converts a queried AppsModel to a usable dictionary for the JSON API."""
    return {
        "category": app.category,
        "coder": app.author.display_name,
        "contributors": app.meta_data.contributors,
        "display_name": app.meta_data.display_name,
        "downloads": 0,
        "extra_directories": [],
        "extracted": 0,
        "icon_url": "",
        "internal_name": app.slug,
        "long_description": app.meta_data.long_description,
        "package_type": "dol",
        "rating": "",
        "release_date": 0,
        "short_description": app.meta_data.short_description,
        "updated": 0,
        "version": app.meta_data.display_version,
        "zip_size": 0,
        "zip_url": "",
    }
