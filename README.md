# Common CI/CD workflows for use by Data Insights Team

Contains reusable code for github actions

## Github Reusable Actions

These reusable actions live in `.github/workflows`.
For more information about using reusable workflows see [Github's Documentation](https://docs.github.com/en/actions/using-workflows/reusing-workflows).

### `python_code_quality.yml`

This workflow runs various checks for code quality purposes, including formatting and running tests.

Example:

```yaml
name: Code Quality
on:
  push:
    branches:
      - development
      - main
  pull_request:
jobs:
  reusable_workflow:
    uses: tetrascience/ts-data-insights-ci-cd-common/.github/workflows/python_code_quality.yml@main
    with:
      python-version: 3.7
    secrets:
      CODACY_PROJECT_TOKEN: "${{ secrets.CODACY_PROJECT_TOKEN }}"
```

**NOTES**

- You need to provide the python version you are running with, otherwise linting and other tools could fail
- The linting and formatting tools will use the configurations in your repo.
  For example, if you want to configure `pytest`, then you will need to set those configurations in `your_repo/.pyproject.toml`

### `publish.yml`

This workflow runs a github action to publish a task-script from its repo.
The github action being called is in [ts-deploy-task-script-action](https://github.com/tetrascience/ts-deploy-task-script-action).
See the documentation in the action's repository for more information on what it does.

Example:

```yaml
name: Publish
on: ["push", "pull_request"]

jobs:
  publish:
    uses: tetrascience/ts-data-insights-ci-cd-common/.github/workflows/publish.yml@main
    with:
      namespace: "SOME_NAMESPACE"
      slug: "SOME_SLUG"

    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.ARTIFACT_BUILD_AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.ARTIFACT_BUILD_AWS_SECRET_ACCESS_KEY }}
      ssh_key: ${{ secrets.ARTIFACT_BUILD_GITHUB_SSH_KEY }}
```

## Github Actions

These actions live in `.github/actions`.
Actions differ from reusable workflows and are defined differently
For more information on writing actions see [Github's Documentation](https://docs.github.com/en/actions/creating-actions/about-custom-actions)

### deprecation-checker

This action run custom pylint plugins and checkers to flag deprecated code.
It is used as a step in the `python_code_quality` reusable workflow above.

Deprecated code being checked:

| Pylint message ID | Pylint message symbol    | Description                                                                                      |
| ----------------- | ------------------------ | ------------------------------------------------------------------------------------------------ |
| `W1599`           | `deprecated-context-api` | This flags instances of context.write_file() which have a `file_category="IDS"` keyword argument |
| TBD               |                          |                                                                                                  |
