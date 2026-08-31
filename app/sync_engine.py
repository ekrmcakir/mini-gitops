import os
import yaml
import git
from pathlib import Path
from app.config import settings
from app.models import DesiredState

class GitSyncEngine:
    """Handles Git clone, fetch, and manifest file parsing."""

    def __init__(self, repo_url: str = settings.GIT_REPO_URL, target_dir: str = settings.LOCAL_REPO_DIR):
        self.repo_url = repo_url
        self.target_dir = Path(target_dir)

    def sync_repository(self, commit_sha: str | None = None) -> None:
        """Clones or fetches the repository. Falls back to local directory if dummy URL is used."""
        # Check if dummy/example repo URL is configured
        if "example/mini-gitops" in self.repo_url:
            # Running in local development mode (skip external git clone)
            return

        if not self.target_dir.exists():
            self.target_dir.mkdir(parents=True, exist_ok=True)
            repo = git.Repo.clone_from(self.repo_url, self.target_dir, branch=settings.REPO_BRANCH)
        else:
            repo = git.Repo(self.target_dir)
            origin = repo.remotes.origin
            origin.fetch()

        if commit_sha:
            repo.git.checkout(commit_sha)
        else:
            repo.git.checkout(f"origin/{settings.REPO_BRANCH}")

    def parse_manifest(self, manifest_relative_path: str = "manifests/sample-app.yaml") -> DesiredState:
        """Parses the YAML manifest file into a DesiredState model."""
        # Try local project manifests directory first, then target_dir
        local_project_manifest = Path.cwd() / manifest_relative_path
        target_dir_manifest = self.target_dir / manifest_relative_path

        manifest_file = local_project_manifest if local_project_manifest.exists() else target_dir_manifest

        if not manifest_file.exists():
            raise FileNotFoundError(f"Manifest not found at {manifest_file}")

        with open(manifest_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return DesiredState(**data)