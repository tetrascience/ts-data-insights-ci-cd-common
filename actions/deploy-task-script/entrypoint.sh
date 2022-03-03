#!/bin/sh

echo "--- ENV ---"
env
# echo "${INPUT_SSH_KEY}" > /root/.ssh/id_rsa
# chmod 600 /root/.ssh/id_rsa
# cat /root/.ssh/id_rsa
# touch /root/.ssh/known_hosts && ssh-keyscan github.com >> /root/.ssh/known_hosts

echo "--- ARGS ---"
echo $*
echo "MOUNTED WORKSPACE: $GITHUB_WORKSPACE"
# cd /usr/abc_test/
# yarn install --frozen-lockfile --prod
# yarn run publish $PWD
