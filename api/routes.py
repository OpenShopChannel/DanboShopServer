from typing import Dict

from api.apps import app_to_dict
from models import AppsModel, AuthorModel
from repos import REPOS, valid_repo
from flask import Blueprint, abort, jsonify, request

api = Blueprint('api', __name__, template_folder='templates')


@api.get("/v2/hosts")
def retrieve_hosts():
    repo_names: [str] = []
    repositories: Dict[str, Dict] = {}

    for repo_id, repo in REPOS.items():
        # Keep track of this repo's name.
        repo_names.append(repo_id)

        repositories[repo_id] = {
            "description": repo.description,
            "host": repo.host,
            "name": repo.name,
        }

    return {
        "repos": repo_names,
        "repositories": repositories,
    }


@api.get("/v2/<repo>/packages")
def retrieve_package(repo):
    # Ensure this is a valid repo.
    if not valid_repo(repo):
        abort(404)

    single_package = False

    # Check whether we are querying a single app,
    # a category, a specific author, or all apps.
    statement = AppsModel.query

    # Common query parameters
    coder = request.args.get("coder")
    category = request.args.get("category")
    package = request.args.get("package")

    if category:
        statement = statement.where(AppsModel.category == category)

    if coder:
        statement = statement.where(AuthorModel.display_name == coder)

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
