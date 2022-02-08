# Common CI/CD workflows for use by Data Insights Team

Contains reusable code for both github actions and Travis-CI

## Github Reusable Actions

To use one of the actions specified here, create a YAML file in `.github/workflows/` in your repo.
Call the reusable action with the following snippet.

```yaml
name: Code Quality
on: pull_request
jobs:
  reusable_workflow:
    uses: tetrascience/ts-data-insights-ci-cd-common/.github/workflows/python_code_quality@main
    with:
      python-version: 3.7
      run_tests: true
```

The `run_tests` input defaults to `false` and is optional for the time being. It will default to true in the future.

You can also include this as a job within existing workflows if you wish.

**NOTES**

- You may want to pin the version to a tag instead of `main`.
  This will pull the given git ref from this repository.
- You need to provide the python version you are running with, otherwise linting and other tools could fail
- The linting and formatting tools will use the configurations in your repo.
  For example, if you want to configure `flake8`, then you will need to set those configurations in `your_repo/.flake8`

## Travis CI

** TBD **
