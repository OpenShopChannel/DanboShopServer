import os
from enum import Enum

import config


class StorageTypes(Enum):
    """Possible types for storage on disk."""
    ZIPPED = "zipped"
    UNZIPPED = "unzipped"
    ICONS = "icons"


class FileTypes(Enum):
    """Possible types for files downloaded or requested."""
    ZIP = "zip"
    ICON = "png"


def storage_dir(storage_type: StorageTypes) -> str:
    """Returns a path for a given subpath in the configured storage directory."""
    return f"{config.FILE_STORAGE_PATH}/{str(storage_type)}"


def file_path(file_name: str, file_type: FileTypes) -> str:
    """Returns a path for a file type within the given storage type."""
    if file_type == FileTypes.ICON:
        storage_type = StorageTypes.ICONS
    elif file_type == FileTypes.ZIP:
        storage_type = StorageTypes.ZIPPED
    else:
        raise ValueError

    return storage_dir(storage_type) + "/" + file_name + "." + str(file_type)


def create_storage_dirs():
    """Creates storage directories for all available types, if necessary."""
    for storage_type in StorageTypes:
        dir_path = storage_dir(storage_type)
        os.makedirs(dir_path, exist_ok=True)
