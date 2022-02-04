import hashlib
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
    return os.path.join(config.FILE_STORAGE_PATH, storage_type.value)


def storage_path(storage_type: StorageTypes, dir_name: str) -> str:
    """Returns a path for a directory within the given storage type."""
    return os.path.join(storage_dir(storage_type), dir_name)


def storage_type_for_file(file_type: FileTypes) -> StorageTypes:
    """Returns the storage type associated with a file type."""
    if file_type == FileTypes.ICON:
        storage_type = StorageTypes.ICONS
    elif file_type == FileTypes.ZIP:
        storage_type = StorageTypes.ZIPPED
    else:
        raise ValueError

    return storage_type


def file_path(file_name: str, file_type: FileTypes) -> str:
    """Returns a path for a file type within the given storage type."""
    storage_type = storage_type_for_file(file_type)
    full_file_name = file_name + "." + file_type.value

    return os.path.join(storage_dir(storage_type), full_file_name)


def create_storage_dirs():
    """Creates storage directories for all available types, if necessary."""
    for storage_type in StorageTypes:
        dir_path = storage_dir(storage_type)
        os.makedirs(dir_path, exist_ok=True)


def md5sum_file(path: str) -> bytes:
    """Returns the MD5 hash of a file."""
    with open(path, 'rb') as file:
        contents = file.read()
        digest = hashlib.md5(contents).digest()

    return digest


def sha256sum_file(path: str) -> bytes:
    """Returns the SHA-256 hash of a file."""
    with open(path, 'rb') as file:
        contents = file.read()
        digest = hashlib.sha256(contents).digest()

    return digest
