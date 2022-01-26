from typing import Dict

from repos import REPOS
from flask import Blueprint

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
