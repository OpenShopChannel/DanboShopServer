from flask import Blueprint

import config
from admin.create_application import import_for

admin = Blueprint('admin', __name__, template_folder='templates')


if config.allow_import:
    @admin.get("/v2/admin/import")
    def temporary_import():
        """Temporary route to assist importing"""
        import_for("primary")
        import_for("themes")

        return {"success": True}
