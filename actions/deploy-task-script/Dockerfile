FROM node:16

RUN mkdir -p /usr/abc_test/ && mkdir -p /root/.ssh/
COPY package.json yarn.lock index.js entrypoint.sh /usr/abc_test/

RUN chmod +x /usr/abc_test/entrypoint.sh

ENTRYPOINT ["/usr/abc_test/entrypoint.sh"]
