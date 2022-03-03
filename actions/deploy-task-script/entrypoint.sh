#!/bin/sh
echo "::group::START ENV"
env
echo "::endgroup"

echo "::group::Setup Action"

# add the provided SSH key and install the deployer
# we need to do this step in the dockerfile because it requires SSH access to download the builder library
echo "${INPUT_SSH_KEY}" > /root/.ssh/id_rsa
chmod 600 /root/.ssh/id_rsa

cd /usr/local/deploy_task_script
yarn install --frozen-lockfile --prod

# Install package for use globally
yarn global add $PWD

# Run the package in the current code
cd $GITHUB_WORKSPACE

export AWS_ACCESS_KEY_ID=${INPUT_AWS_ACCESS_KEY}
export AWS_SECRET_ACCESS_KEY=${INPUT_AWS_ACCESS_KEY_SECRET}

# FIXME: these should not be hard coded!
echo "::endgroup::"

echo "::group::GOTIME ENV"
env
echo "::endgroup::"

deploy-task-script
