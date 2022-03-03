#!/bin/sh
yarn version

echo "${INPUT_SSH_KEY}" > /root/.ssh/id_rsa
chmod 600 /root/.ssh/id_rsa
# cat /root/.ssh/id_rsa

cd /usr/abc_test/
yarn install --frozen-lockfile --prod
yarn global add $PWD

cd $GITHUB_WORKSPACE
deploy-task-script
