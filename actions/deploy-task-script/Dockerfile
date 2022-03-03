FROM node:16

RUN mkdir -p /usr/abc_test/ && \
    mkdir -p /root/.ssh/ && \
    touch /root/.ssh/known_hosts && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts

COPY package.json yarn.lock index.js entrypoint.sh /usr/abc_test/

RUN chmod +x /usr/abc_test/entrypoint.sh

ENTRYPOINT ["/usr/abc_test/entrypoint.sh"]
