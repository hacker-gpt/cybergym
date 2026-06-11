FROM node:22 AS installer
COPY . /cybergym
WORKDIR /cybergym
RUN npm i -g typescript ts-node
RUN npm install --omit=dev --unsafe-perm
RUN npm dedupe --omit=dev
RUN rm -rf frontend/node_modules
RUN rm -rf frontend/.angular
RUN rm -rf frontend/src/assets
RUN mkdir logs
RUN chown -R 65532 logs
RUN chgrp -R 0 ftp/ frontend/dist/ logs/ data/ i18n/
RUN chmod -R g=u ftp/ frontend/dist/ logs/ data/ i18n/
RUN rm data/chatbot/botDefaultTrainingData.json || true
RUN rm ftp/legal.md || true
RUN rm i18n/*.json || true

ARG CYCLONEDX_NPM_VERSION=latest
RUN npm install -g @cyclonedx/cyclonedx-npm@$CYCLONEDX_NPM_VERSION
RUN npm run sbom

FROM gcr.io/distroless/nodejs22-debian12
ARG BUILD_DATE
ARG VCS_REF
LABEL maintainer="HackerGPT" \
    org.opencontainers.image.title="CyberGym" \
    org.opencontainers.image.description="An intentionally insecure web application for security training and CTFs" \
    org.opencontainers.image.authors="HackerGPT, based on OWASP Juice Shop by Bjoern Kimminich" \
    org.opencontainers.image.vendor="HackerGPT" \
    org.opencontainers.image.documentation="https://github.com/hacker-gpt/cybergym" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.version="19.1.1" \
    org.opencontainers.image.url="https://github.com/hacker-gpt/cybergym" \
    org.opencontainers.image.source="https://github.com/hacker-gpt/cybergym" \
    org.opencontainers.image.revision=$VCS_REF \
    org.opencontainers.image.created=$BUILD_DATE
WORKDIR /cybergym
COPY --from=installer --chown=65532:0 /cybergym .
USER 65532
EXPOSE 3000
CMD ["/cybergym/build/app.js"]
