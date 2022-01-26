from dataclasses import dataclass
from typing import Dict


@dataclass
class Repo(object):
    """Class representing information for a HBB repo."""

    description: str
    name: str
    host: str


"""A dictionary of available repositories to download software from."""
REPOS: Dict[str, Repo] = {
    "primary": Repo(
        description="The official Open Shop Channel Homebrew Apps repository.",
        name="Open Shop Channel",
        host="hbb1.oscwii.org",
    ),
    "themes": Repo(
        description="The official Open Shop Channel Homebrew Channel Themes repository.",
        name="Homebrew Channel Themes",
        host="hbb3.oscwii.org",
    ),
}
