#!/usr/bin/env node

const { program } = require('commander');
const { appDistribution } = require('../firebase.app.config');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configure CLI
program
  .version('1.0.0')
  .description('Firebase App Distribution CLI tools');

/**
 * Generate release notes from git commits
 * @param {string} since Git reference to start from
 * @returns {string} Formatted release notes
 */
function generateReleaseNotes(since = 'HEAD~10') {
  try {
    // Get recent commits
    const commits = execSync(`git log ${since}..HEAD --pretty=format:"%h %s"`)
      .toString()
      .split('\n')
      .map(line => `- ${line}`);

    // Get current version
    const version = require('../package.json').version;
    
    // Get build number (using git commit count)
    const buildNumber = execSync('git rev-list --count HEAD')
      .toString()
      .trim();

    return `Version: ${version}
Build: ${buildNumber}

Changes in this version:
${commits.join('\n')}

Known Issues:
- None reported

Feedback:
Please submit feedback through the in-app feedback form or email support@firstcourt.com`;
  } catch (error) {
    console.error('Error generating release notes:', error);
    process.exit(1);
  }
}

// Command: Build and upload
program
  .command('deploy')
  .description('Build and upload app to Firebase Distribution')
  .option('-g, --groups <groups>', 'Comma-separated list of tester groups', 'internal-testers')
  .option('-n, --notes <notes>', 'Path to release notes file')
  .option('-e, --env <env>', 'Environment (development, staging, production)', 'development')
  .action(async (options) => {
    try {
      // Build app
      console.log('Building app...');
      execSync('npm run build', { stdio: 'inherit' });

      // Generate or load release notes
      let releaseNotes;
      if (options.notes && fs.existsSync(options.notes)) {
        releaseNotes = fs.readFileSync(options.notes, 'utf8');
      } else {
        console.log('Generating release notes from commits...');
        releaseNotes = generateReleaseNotes();
      }

      // Upload build
      console.log('Uploading build to Firebase...');
      const groups = options.groups.split(',');
      const buildPath = path.join(__dirname, '../dist/app.zip');
      
      const result = await appDistribution.uploadBuild(buildPath, releaseNotes, groups);
      
      // Notify testers
      console.log('Notifying testers...');
      await appDistribution.notifyTesters(result.buildId, groups);
      
      console.log('Deployment complete!');
      console.log('Build ID:', result.buildId);
      console.log('Groups notified:', groups.join(', '));
    } catch (error) {
      console.error('Deployment failed:', error);
      process.exit(1);
    }
  });

// Command: Manage testers
program
  .command('testers')
  .description('Manage tester groups')
  .option('-a, --add <emails>', 'Add comma-separated email addresses')
  .option('-g, --groups <groups>', 'Comma-separated list of groups', 'internal-testers')
  .action(async (options) => {
    try {
      if (options.add) {
        const emails = options.add.split(',');
        const groups = options.groups.split(',');
        
        console.log('Adding testers:', emails.join(', '));
        console.log('To groups:', groups.join(', '));
        
        await appDistribution.addTesters(emails, groups);
        console.log('Testers added successfully!');
      }
    } catch (error) {
      console.error('Error managing testers:', error);
      process.exit(1);
    }
  });

// Command: Create release notes
program
  .command('notes')
  .description('Generate release notes from git commits')
  .option('-o, --output <file>', 'Output file path')
  .option('-s, --since <commit>', 'Generate from this git reference', 'HEAD~10')
  .action((options) => {
    try {
      const notes = generateReleaseNotes(options.since);
      
      if (options.output) {
        fs.writeFileSync(options.output, notes);
        console.log(`Release notes written to ${options.output}`);
      } else {
        console.log(notes);
      }
    } catch (error) {
      console.error('Error generating release notes:', error);
      process.exit(1);
    }
  });

// Parse command line arguments
program.parse(process.argv);
