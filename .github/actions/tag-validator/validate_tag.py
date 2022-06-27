from typing import Optional

import sh
import semver

class Tag:
    def __init__(self, tag: str, artifact_type: Optional[str] = None):

        _tag = tag[1:] if tag.startswith("v") else tag
        self.tag = semver.VersionInfo.parse(_tag)

        self.artifact_type = artifact_type

    def validate(self):
        self.validate_tag_is_new()
        self.validate_tag_is_not_reserved_for_pull_request()

    def validate_tag_is_new(self):
        existing_tags = sh.git("tag")
        if existing_tags:
            existing_tags = existing_tags.split("\n")
            if self.tag in existing_tags:
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


if __name__ == "__main__":
    print("Validate tag here")