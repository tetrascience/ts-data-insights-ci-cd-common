#!/bin/sh

echo "${INPUT_SSH_KEY}" > /root/.ssh/id_rsa
chmod 600 /root/.ssh/id_rsa
# cat /root/.ssh/id_rsa

echo "MOUNTED WORKSPACE: $GITHUB_WORKSPACE"

cd /usr/abc_test/
# git clone git@github.com/tetrascience/ts-lib-artifact-builder --depth=1
yarn install --frozen-lockfile --prod
yarn run publish $GITHUB_WORKSPACE
