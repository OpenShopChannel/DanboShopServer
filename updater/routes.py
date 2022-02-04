from flask import Blueprint

from updater.process import check_for_update, update_app
from models import AppsModel

updater = Blueprint('updater', __name__, template_folder='templates')


# All temporary routes
@updater.get("/v2/updater/check")
def check_updates():
    """Check for updates"""
    apps: [AppsModel] = AppsModel.query.all()
    updates = {}
    for app in apps:
        updates[app.slug] = check_for_update(app.slug)
    return updates


@updater.get("/v2/updater/update")
def update_all():
    """Update all outdated apps"""
    updated = {}
    for app in check_updates():
        updated[app] = update_app(app)
    return updated
