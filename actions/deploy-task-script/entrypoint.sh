#!/bin/sh
echo "::group::ENV"
env
echo "::endgroup"

echo "::group::Setup Action"
echo "${INPUT_SSH_KEY}" > /root/.ssh/id_rsa
chmod 600 /root/.ssh/id_rsa

# we need to do this step in the dockerfile because it requires SSH access to download the builder library
cd /usr/local/deploy_task_script
yarn install --frozen-lockfile --prod

# Install package for use globally
yarn global add $PWD

# Run the package in the current code
cd $GITHUB_WORKSPACE

export AWS_ACCESS_KEY_ID=${INPUT_AWS_ACCESS_KEY_ID}
export AWS_SECRET_ACCESS_KEY=${INPUT_AWS_SECRET_ACCESS_KEY}
export ARTIFACT_BUCKET=${INPUT_ARTIFACT_BUCKET}
export ARTIFACT_PREFIX=${INPUT_ARTIFACT_PREFIX}


# FIXME: these should not be hard coded!
export NAMESPACE='common'
export SLUG='abs-test-task'
export VERSION='v0.1.3'
echo "::endgroup::"

deploy-task-script
