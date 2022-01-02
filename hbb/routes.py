from flask import Blueprint, Response, stream_with_context, request
from pip._vendor import requests

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
    Returns the rating of an app.
    """
    app_name = request.args.get("name")
    esid = request.args.get("esid")
    return "2 5"


# Stub
@hbb.route('/hbb/repo_list.txt')
def repo_list():
    """
    Returns a list of all the repos in the homebrew browser repos list format.
    """
    return """1
Open Shop Channel
hbb1.oscwii.org
/hbb/homebrew_browser/listv036.txt
/hbb/
CodeMii
hbb2.oscwii.org
/hbb/homebrew_browser/listv036.txt
/hbb/
Homebrew Channel Themes
hbb3.oscwii.org
/hbb/homebrew_browser/listv036.txt
/hbb/"""
