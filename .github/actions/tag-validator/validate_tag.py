import os
import re
from typing import Optional

import sh
import semver

class Tag:
    def __init__(self, tag: str, artifact_type: Optional[str] = None):

        self.tag = tag[1:] if tag.startswith("v") else tag
        self.artifact_type = artifact_type

    def validate(self):
        self.validate_sem_version()
        self.validate_tag_is_new()
        self.validate_tag_is_not_reserved_for_pull_request()
        print(f"Tag validation complete for {self.tag}")

    def validate_tag_is_new(self):
        existing_tags = sh.git("tag")
        if existing_tags:
            existing_tags = existing_tags.split("\n")
            if f"v{self.tag}" in existing_tags:
                raise ValueError(f"Tag {self.tag} already exist.")

    def validate_tag_is_not_reserved_for_pull_request(self):
        if (
            self.tag.major == 0
            and self.tag.minor == 0
        ):
            raise ValueError(
                f"Tag: {str(self.tag)} is reserved for pull request."
                "Major and minor version can not be zero."
            )

    def validate_sem_version(self):
        build_version_patter = r'\d+.\d+.\d+.\d+$'
        if re.match(build_version_patter, self.tag):
            return

        try:
            semver.VersionInfo.parse(self.tag)
        except Exception as e:
            raise ValueError(f"Invalid tag versioning: {self.tag}")


if __name__ == "__main__":
    gh_tag = os.environ["GITHUB_REF_NAME"]
    tag = Tag(gh_tag)
    tag.validate()

