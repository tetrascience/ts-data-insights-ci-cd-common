#!/usr/bin/env node

const core = require("@actions/core");

const fs = require("fs");
const Path = require("path");
const _ = require("lodash");
const simpleGit = require("simple-git");

const { spawn } = require("child_process");
const { getBuilder } = require("ts-lib-artifact-builder");
const UpdateListUtil = require("ts-lib-artifact-builder/helper/update-list");
const {
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
  const commit = git.revparse(["--short", "HEAD"]);
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
};

// --- MAIN METHOD ---
const publish = async () => {
  console.time("TOTAL");
  const meta = await core.group("get code meta", getCodeMeta);
  console.info("CODE META:");
  console.info(meta);
  console.timeEnd("TOTAL");
  core.notice("all done!");
};

publish();
