import os

from flask import Response, send_file, abort

from utils import slug_file_uuid, FileTypes


def serve_slug_icon(slug: str) -> Response:
    """Serves an icon for the given slug, returning a missing image if not possible."""
    filename = slug_file_uuid(slug, FileTypes.ICON)
    if os.path.isfile(filename):
        return send_file(filename, mimetype='image/png')

    # Fallback icon
    return send_file("static/images/missing-app-icon.png", mimetype='image/png')


def serve_slug_file(slug: str, file_type: FileTypes):
    """Serves the given file type for the passed slug, returning 404 if not possible."""
    filename = slug_file_uuid(slug, file_type)
    if os.path.isfile(filename):
        return send_file(filename)
    else:
        abort(404)
