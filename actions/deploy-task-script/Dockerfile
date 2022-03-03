FROM node:16

RUN mkdir -p /usr/local/deploy_task_script/ && \
    mkdir -p /root/.ssh/ && \
    touch /root/.ssh/known_hosts && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts

COPY package.json yarn.lock index.js entrypoint.sh /usr/local/deploy_task_script/

RUN chmod +x /usr/local/deploy_task_script/entrypoint.sh

ENTRYPOINT ["/usr/local/deploy_task_script/entrypoint.sh"]
