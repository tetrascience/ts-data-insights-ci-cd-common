#!/usr/bin/env node

const core = require("@actions/core");

const fs = require("fs");
const Path = require("path");
const _ = require("lodash");
const simpleGit = require("simple-git");

const { getBuilder } = require("ts-lib-artifact-builder");
const UpdateListUtil = require("ts-lib-artifact-builder/helper/update-list");
const {
  NAMESPACE,
  SLUG,
  VERSION,
  PUSH_TO_ECR,
  ARTIFACT_BUCKET,
  ARTIFACT_PREFIX,
  SSH_KEY_PATH,
  COMMIT,
  GITHUB_JOB,
  GITHUB_RUN_ID,
  GITHUB_RUN_NUMBER,
  GITHUB_RUN_ATTEMPT,
  GITHUB_SHA,
  GITHUB_REPOSITORY,
} = process.env;

// FIXME: add tests with jest or something similar?
// TODO: reorganize so these get put into src files
const getCodeMeta = _.once(async () => {
  const git = simpleGit();
  const commit = await git.revparse(["--short", "HEAD"]);
  const curTags = (await git.tag({ "--points-at": "HEAD" })).trim().split("\n");
  console.log(`Found tags that point at HEAD: ${curTags}`);
  return {
    commit,
    githubData: {
      action: true,
      job: GITHUB_JOB,
      run: {
        id: GITHUB_RUN_ID,
        number: GITHUB_RUN_NUMBER,
        attempt: GITHUB_RUN_ATTEMPT,
      },
      repository: GITHUB_REPOSITORY,
      sha: GITHUB_SHA,
    },
    tags: curTags,
    createdAt: new Date().toISOString(),
  };
});

const buildit = async () => {
  const cfg = {
    source: ".",
    namespace: NAMESPACE,
    slug: SLUG,
    version: VERSION,
    type: "task-scripts",
    pushToEcr: PUSH_TO_ECR || false,
    buildRecordMeta: await getCodeMeta(),
    shouldUpdateList: false,
    saveBuildLog: true,
    sshPrivateKeyPath: "/root/.ssh/id_rsa",
  };
  console.log("--- Build config ---");
  console.log(cfg);
  const builder = getBuilder(cfg);
  console.log("--- list bucket ---");
  const { bucket, prefix, endpoint } = builder.getLocation();
  await listBucket(endpoint, bucket, prefix);
};

const listBucket = async (endpoint, bucket, prefix) => {
  const ulu = new UpdateListUtil({
    endpoint,
    bucket,
    prefix,
  });
  console.time("scan artifacts");
  const scan = await ulu.scanArtifacts("task-scripts");
  console.endTime("scan artifacts");
  console.time("read list");
  const list = await ulu.readArtifactList("task-scripts");
  console.endTime("read list");
};

// --- MAIN METHOD ---
const publish = async () => {
  console.time("TOTAL");
  const meta = await getCodeMeta();
  console.info("CODE META:");
  console.info(meta);
  await core.group("build it", buildit);
  console.timeEnd("TOTAL");
  core.notice("all done!");
};

// FIXME: make this run only when main.  (see list updater)
console.log(process.env);
publish();
