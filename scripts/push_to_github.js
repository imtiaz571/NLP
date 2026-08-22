// Script to push current committed code to GitHub using isomorphic-git
const fs = require('fs');
const path = require('path');

let git, http;
try {
  git = require('isomorphic-git');
  http = require('isomorphic-git/http/node');
} catch (e) {
  try {
    const tempNodeModules = path.join(process.env.LOCALAPPDATA || process.env.TEMP, 'Temp', 'nodegit', 'node_modules');
    git = require(path.join(tempNodeModules, 'isomorphic-git'));
    http = require(path.join(tempNodeModules, 'isomorphic-git', 'http', 'node'));
  } catch (e2) {
    const fallbackPath = 'C:/Users/imtia/AppData/Local/Temp/nodegit/node_modules/isomorphic-git';
    git = require(fallbackPath);
    http = require(path.join(fallbackPath, 'http/node'));
  }
}

async function push() {
  const token = process.argv[2] || process.env.GITHUB_TOKEN;
  if (!token) {
    console.error('Error: Please provide your GitHub Personal Access Token.');
    console.error('Usage: node scripts/push_to_github.js <YOUR_GITHUB_TOKEN>');
    process.exit(1);
  }

  const projectDir = path.resolve(__dirname, '..');
  console.log(`Pushing repository from: ${projectDir}`);
  console.log('Target: https://github.com/imtiaz571/NLP (branch: main)');

  try {
    const pushResult = await git.push({
      fs,
      http,
      dir: projectDir,
      remote: 'origin',
      ref: 'main',
      onAuth: () => ({
        username: token,
        password: ''
      })
    });
    console.log('Push completed successfully!', pushResult);
  } catch (err) {
    console.error('Push failed:', err.message);
    if (err.data) console.error(err.data);
    process.exit(1);
  }
}

push();
