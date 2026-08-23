// Helper script to push repository to GitHub
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

async function push() {
  const token = process.argv[2] || process.env.GITHUB_TOKEN;
  const projectDir = path.resolve(__dirname, '..');
  
  console.log(`Pushing repository from: ${projectDir}`);
  console.log('Target: https://github.com/imtiaz571/NLP (branch: main)');

  let gitCmd = 'git';
  const standardGitPath = 'C:\\Program Files\\Git\\cmd\\git.exe';
  if (fs.existsSync(standardGitPath)) {
    gitCmd = `"${standardGitPath}"`;
  }

  try {
    const remoteUrl = token
      ? `https://${token}@github.com/imtiaz571/NLP.git`
      : 'origin';
    
    console.log('Executing git push...');
    execSync(`${gitCmd} push ${remoteUrl} main`, {
      cwd: projectDir,
      stdio: 'inherit'
    });
    console.log('\n[SUCCESS] Repository successfully pushed to GitHub!');
  } catch (err) {
    console.error('\n[ERROR] Git push failed:', err.message);
    process.exit(1);
  }
}

push();
