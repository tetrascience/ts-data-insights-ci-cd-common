import os
import re
from sys import pycache_prefix
from typing import Optional

import sh
import semver
import jsonref
from loguru import logger


class TagVersionValidator:
    def __init__(self, tag: str, artifact_type: Optional[str] = None):
        self.tag = tag[1:] if tag.startswith("v") else tag
        self.artifact_type = artifact_type

    def __call__(self):
        self.validate()

    def validate(self):
        self.validate_sem_version()
        self.validate_current_tag_bump()
        self.validate_tag_is_not_reserved_for_pull_request()
        self.validate_tag_in_artifact_files()

        logger.info(f"Tag validation completed sucessfully for {self.tag}")

    def validate_tag_is_new(self):
        existing_tags = sh.git("tag")
        if existing_tags:
            existing_tags = existing_tags.split("\n")
            if f"v{self.tag}" in existing_tags:
                raise ValueError(f"Tag {self.tag} already exist.")

    def validate_tag_is_not_reserved_for_pull_request(self):
        tag = semver.VersionInfo.parse(self.tag)
        if tag.major == 0 and tag.minor == 0:
            raise ValueError(
                f"Tag: {str(self.tag)} is reserved for pull request. "
                "Major and minor version can not be zero."
            )

    def validate_current_tag_bump(self):
        last_tag = None
        git_tags = sh.git("tag", "--sort=-creatordate")

        if git_tags:
            last_tag = git_tags.split("\n")[0]
            last_tag = last_tag[1:] if last_tag.startswith("v") else last_tag

        if last_tag:
            next_tag_options = self.get_options_for_next_tag(last_tag)
            if self.tag not in next_tag_options:
                raise ValueError(
                    f"Invalid tag: {self.tag}. "
                    f"Possible option for the bumped tag versions are: {next_tag_options} "
                    f"as the last tag is {last_tag}"
                )
        else:
            logger.info(
                f"Could find any existing tag. Validation will continue for tag = {self.tag}"
            )

    def validate_sem_version(self):
        build_version_pattern = r"\d+.\d+.\d+.\d+$"
        if re.match(build_version_pattern, self.tag):
            return

        try:
            semver.VersionInfo.parse(self.tag)
        except Exception as e:
            raise ValueError(f"Invalid tag versioning: {self.tag}")

    def validate_tag_in_artifact_files(self):
        if self.type == "task-script":
            self._check_version_in_pyproject()
        if self.type == "ids":
            self._check_version_in_schema_json()

    def _check_version_in_pyproject(self):
        py_project_path = "./pyproject.toml"
        if not os.path.exists(py_project_path):
            raise FileNotFoundError("Could not find pyproject.toml")

        with open(py_project_path, "r") as py_proj:
            for line in py_proj:
                if line.startswith("version = "):
                    py_project_tag = line.split("=")[1]
                    py_project_tag = py_project_tag.replace('"', "")
                    py_project_tag = py_project_tag.strip()
                    if py_project_tag != self.tag:
                        raise ValueError(
                            "Version Mismatch."
                            f"Tag version = {self.tag}. "
                            f"Version in pyproject.toml = {py_project_tag}"
                        )
                    return

    def _check_version_in_schema_json(self):
        schema_json_path = "./schema.json"
        if not os.path.exists(schema_json_path):
            raise FileNotFoundError("Could not find schema.json")

        with open(schema_json_path, "r") as schema_json:
            schema = jsonref.load(schema_json)

            # Check version in ID
            id_ = schema["$id"]
            tag_in_id = id_.split("/")[-2][1:]
            if self.tag != tag_in_id:
                raise ValueError(f"Invalid tag in $id: {id_}. It should be {self.tag}.")

            # Check version property
            properties = schema.get("properties")
            if not properties:
                raise KeyError("schema.json does not have top level properties")

            ids_version = properties.get("@idsVersion")
            if not ids_version:
                raise KeyError("'@idsVersion' is not defined in schema.json")

            if ids_version != self.tag:
                raise ValueError(
                    f"'@idsVersion' is invalid: {ids_version}. "
                    f"It should be {self.tag}"
                )

    @staticmethod
    def get_options_for_next_tag(last_tag: str):
        doc_build_version = None
        build_version_pattern = r"\d+.\d+.\d+.\d+$"
        tag = last_tag
        if re.match(build_version_pattern, last_tag):
            tag = last_tag.split(".")
            doc_build_version = tag[-1]
            tag = ".".join(tag[:3])

        tag = semver.VersionInfo.parse(tag)
        possible_next_versions = [
            str(tag.bump_major()),
            str(tag.bump_minor()),
            str(tag.bump_patch()),
        ]

        if doc_build_version:
            next_doc_build_version = int(doc_build_version) + 1
            next_version_with_doc_build = str(tag) + f".{next_doc_build_version}"
            possible_next_versions.append(next_version_with_doc_build)

        return possible_next_versions


def get_artifact_type(repo: str) -> str:
    if "task-script" in repo.lower():
        artifact_type = "task-script"
    elif "protocol" in repo.lower():
        artifact_type = "master-script"
    elif "IDS" in repo.lower():
        artifact_type = "task-script"
    else:
        artifact_type = None

    if artifact_type is None:
        raise ValueError(
            f"Invalid Repository Name: {repo}. "
            "Make sure it follows Tetrascience naming conventions for artifacts."
        )
    return artifact_type


if __name__ == "__main__":
    gh_tag = os.environ["GITHUB_REF_NAME"]
    repo_name = os.environ["GITHUB_REPOSITORY"]
    artifact_type = get_artifact_type(repo_name)
    TagVersionValidator(gh_tag, artifact_type)()
