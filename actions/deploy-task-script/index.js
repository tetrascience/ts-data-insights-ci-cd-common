const Path = require("path");
const _ = require("lodash");
const { spawn } = require("child_process");

// FIXME: add tests with jest or something similar?
// TODO: reorganize so these get put into src files
const exec = async (cmd, args, options = { resolveStdout: false }) => {
  console.log("Running:", [cmd, ...args].join(" "));
  const { resolveStdout } = options;
  return new Promise((res, rej) => {
    const cp = spawn(cmd, args, options);
    let stdout = "";

    cp.stdout.on("data", (data) => {
      console.log(`stdout: ${data}`);
      if (resolveStdout) {
        stdout += data;
      }
    });

    cp.stderr.on("data", (data) => {
      console.log(`stderr: ${data}`);
    });

    cp.on("close", (code) => {
      console.log(`child process exited with code ${code}`);
      if (code) {
        rej(new Error("Non-zero exit code"));
      }
      res(stdout);
    });
  });
};

const getCodeMeta = _.once(async () => {
  const commit = (
    await exec("git", ["rev-parse", "--short", "HEAD"], {
      resolveStdout: true,
    })
  ).trim();
  return {
    commit,
    createdAt: new Date().toISOString(),
  };
});

// --- MAIN METHOD ---
const publish = async () => {
  const [node, script, input] = process.argv;
  console.log(process.argv);
  console.log(`APP: ${script} PWD: ${input}`);
  console.time("TOTAL");
  const meta = await getCodeMeta();
  console.info("CODE META:");
  console.info(meta);
  console.timeEnd("TOTAL");
};

publish();
