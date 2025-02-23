#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

function generateReleaseNotes() {
  // Get latest git commit hash and message
  const commitHash = execSync('git rev-parse HEAD').toString().trim();
  const commitMessage = execSync(`git log -1 --pretty=%B`).toString().trim();
  
  // Get current date
  const currentDate = new Date().toISOString();
  
  // Collect information about changes
  const changedFiles = execSync('git diff --name-only HEAD^').toString().trim().split('\n');
  
  // Create release notes
  const releaseNotes = {
    version: process.env.npm_package_version,
    date: currentDate,
    commitHash,
    commitMessage,
    changedFiles,
    buildInfo: {
      environment: process.env.NODE_ENV || 'development',
      timestamp: Date.now()
    }
  };
  
  // Write release notes to file
  const outputDir = path.join(process.cwd(), 'dist');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
  }
  
  const outputFile = path.join(outputDir, 'release-notes.json');
  fs.writeFileSync(outputFile, JSON.stringify(releaseNotes, null, 2));
  
  console.log(`Release notes generated: ${outputFile}`);
  return releaseNotes;
}

// Run the script if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  generateReleaseNotes();
}

export default generateReleaseNotes;
