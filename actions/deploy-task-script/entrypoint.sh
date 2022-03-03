#!/bin/sh
yarn version

echo "${INPUT_SSH_KEY}" > /root/.ssh/id_rsa
chmod 600 /root/.ssh/id_rsa
# cat /root/.ssh/id_rsa

echo "MOUNTED WORKSPACE: $GITHUB_WORKSPACE"
pwd
cd /usr/abc_test/
# git clone git@github.com/tetrascience/ts-lib-artifact-builder --depth=1
yarn install --frozen-lockfile --prod
yarn link

cd $GITHUB_WORKSPACE
ls -altr
yarn install
yarn link abc_test
