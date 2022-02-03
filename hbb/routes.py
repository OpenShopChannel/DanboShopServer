from flask import Blueprint, Response, stream_with_context, request
from pip._vendor import requests

from hbb.normalize import Normalize
from models import ReposModel

hbb = Blueprint('hbb', __name__, template_folder='templates')


# Stub
@hbb.route('/hbb/homebrew_browser/listv036.txt')
def apps_list():
    """
    Returns a list of all the apps in the homebrew browser list format.
    """
    req = requests.get("https://hbb1.oscwii.org/hbb/listv036.txt", stream=True)
    return Response(stream_with_context(req.iter_content(chunk_size=1024)), content_type=req.headers['content-type'])


# Stub
@hbb.route('/hbb/get_rating.php')
def get_rating():
    """
    Returns the rating of an app for a user.
    """
    app_name = request.args.get("name")
    esid = request.args.get("esid")
    return "5"


# Stub
@hbb.route('/hbb/update_rating.php')
def update_rating():
    """
    Updates the rating of an app for a user.
    """
    app_name = request.args.get("name")
    esid = request.args.get("esid")
    rating = request.args.get("rating")
    return "5"


# Stub
@hbb.route('/hbb/hbb_download.php')
def register_download():
    """
    Registers that an app was downloaded.
    """
    app_name = request.args.get("name")
    return ""


@hbb.route('/hbb/repo_list.txt')
def repo_list():
    """
    Returns a list of all the repos in the homebrew browser repos list format.
    """
    repos: [ReposModel] = ReposModel.query.all()

    # Add our version, "1", to the response.
    content = Normalize()
    content.add_line("1")

    for repo in repos:
        # Repo's name
        content.add_line(repo.name)
        # Repo's host
        content.add_line(repo.host)
        # Repo's contents
        content.add_line("/hbb/homebrew_browser/listv036.txt")
        # Repo's subdirectory
        content.add_line("/hbb/")

    return content.response
