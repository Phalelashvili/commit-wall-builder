#!/usr/bin/env python3
import logging
import os
from typing import List, Iterable

from git import Repo, Commit
import fire


def find_directories(name, path):
    for root, dirs, files in os.walk(path):
        if name in dirs:
            yield os.path.join(root, name)


class CommitWallBuilder:

    @staticmethod
    def get_commits(repo: Repo) -> Iterable[Commit]:
        config = repo.config_reader()
        actor_name = config.get_value("user", "name")
        actor_email = config.get_value("user", "email")

        for commit in repo.iter_commits("--all"):
            if actor_name == commit.author.name or actor_email == commit.author.email:
                repo_name = CommitWallBuilder.parse_repo_name(commit.repo)
                logging.info("%s %s", repo_name, commit.message)
                yield commit

    def build(self, repo_collection_path: str, target_repo_path: str, file_name: str):
        target_repo = Repo(target_repo_path)

        commits: List[Commit] = []
        for path in find_directories(".git", repo_collection_path):
            logging.debug("found repository %s", path)
            repo = Repo(path)
            if repo.bare:
                logging.warning("ignoring bare repository %s", path)
                continue

            for commit in CommitWallBuilder.get_commits(repo):
                if not any([c.hexsha == commit.hexsha for c in commits]):
                    commits.append(commit)

        commits.sort(key=lambda c: c.committed_datetime)

        file_path = os.path.join(target_repo_path, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

        lines = []
        file_tracked = False
        for commit in commits:
            repo_name = CommitWallBuilder.parse_repo_name(commit.repo)
            line_message = commit.message.split("\n")[0]

            line = f"{commit.committed_datetime} {commit.hexsha} {repo_name} {line_message}\n"
            with open(file_path, "a+", encoding="utf-8") as f:
                f.write(line)

            if not file_tracked:
                target_repo.git.add(".")
                file_tracked = True

            message = f"{repo_name} {commit.message}"
            target_repo.git.commit("-am", message, date=commit.committed_datetime)
            logging.info("commited %s", line_message)

    @staticmethod
    def parse_repo_name(repo: Repo):
        return os.path.basename(repo.working_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fire.Fire(CommitWallBuilder)
