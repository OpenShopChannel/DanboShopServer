import os
from typing import Dict

from api.apps import app_to_dict
from models import AppsModel, AuthorModel, ReposModel
from flask import Blueprint, abort, jsonify, request, send_file

api = Blueprint('api', __name__, template_folder='templates')


@api.get("/v2/hosts")
def retrieve_hosts():
    repos: [ReposModel] = ReposModel.query.all()

    repo_names: [str] = []
    repositories: Dict[str, Dict] = {}

    for repo in repos:
        # Keep track of this repo's name.
        repo_names.append(repo.id)

        repositories[repo.id] = {
            "description": repo.description,
            "host": repo.host,
            "name": repo.name,
        }

    return {
        "repos": repo_names,
        "repositories": repositories,
    }


@api.get("/<repo>/icons/<uuid>.png")
def icon(repo, uuid):
    filename = f"storage/icons/{uuid}.png"
    if os.path.isfile(filename):
        return send_file(filename, mimetype='image/png')

    # fallback icon
    return send_file("static/images/missing-app-icon.png", mimetype='image/gif')


@api.get("/v2/<repo>/packages")
def retrieve_package(repo):
    single_package = False

    # Check whether we are querying a single app,
    # a category, a specific author, or all apps.
    statement = AppsModel.query.where(AppsModel.repo_id == repo)

    # Common query parameters
    coder = request.args.get("coder")
    category = request.args.get("category")
    package = request.args.get("package")

    if category:
        statement = statement.where(AppsModel.category == category)

    if coder:
        statement = statement.where(AuthorModel.display_name == coder)
        statement = statement.where(AppsModel.author_id == AuthorModel.id)

    # We should have a direct package name or a query, one or the other.
    if package:
        # We should only return the exact package - no list.
        single_package = True

        statement = statement.where(AppsModel.slug == package).limit(1)

    # Query!
    queried_apps: [AppsModel] = statement.all()

    # Ensure we have results.
    if len(queried_apps) == 0:
        abort(404)

    # Hold processed apps as a result.
    apps_list: [list] = []

    # Create dictionaries from metadata
    for app in queried_apps:
        app_dict = app_to_dict(app)
        apps_list.append(app_dict)

    # As we create a list, return the first item
    # should we desire a single package.
    if single_package:
        return apps_list[0]
    else:
        return jsonify(apps_list)


@api.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response
