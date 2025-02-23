## First Court

Sistema modular para gestión de procesos judiciales con integración de agentes AI.

### Prerequisites

#### Node.js Version Management

This project requires Node.js 18.x. We recommend using `nvm` (Node Version Manager) to manage Node.js versions:

```bash
# Install NVM (if not already installed)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash

# Use the specified Node.js version
nvm use
```

#### Development Setup

1. Clone the repository
2. Install dependencies

```bash
npm install
```

### Firebase Deployment

#### Preview Channels

Create a new preview channel:

```bash
npm run firebase:channels:create [channelName]
```

List active preview channels:

```bash
npm run firebase:channels:list
```

#### Deployment

Deploy to production:

```bash
npm run deploy:prod
```

Deploy to staging:

```bash
npm run deploy:staging
```

### CI/CD

This project uses GitHub Actions for continuous integration and deployment. Workflows are configured for:

- Firebase Hosting deployment
- Firebase App Distribution
- Build and test validation

#### Required GitHub Secrets

- `FIREBASE_TOKEN`: Firebase CLI authentication token
- `FIREBASE_SERVICE_ACCOUNT`: Service account JSON for Firebase
- `FIREBASE_APP_ID`: Firebase App ID for distribution

### Troubleshooting

#### Node.js Version Compatibility

If you encounter version-related issues, ensure you're using Node.js 18.x:

```bash
node --version  # Should output v18.x.x
npm --version   # Should output 9.x.x or 10.x.x
```

If needed, install the correct Node.js version:

```bash
nvm install 18
nvm use 18
```

### Deployment and Testing Scripts

#### GitHub Secrets Setup

Configure GitHub Actions secrets for CI/CD:

```bash
./scripts/setup-github-secrets.sh
```

#### Firebase App Distribution

Configure tester groups and add testers:

```bash
./scripts/configure-app-distribution.sh
```

#### Deployment Testing

Run comprehensive deployment validation:

```bash
./scripts/test-deployment.sh
```

#### Build Size Monitoring

Current build statistics:

- CSS Bundle: 9.49 kB (gzipped: 2.56 kB)
- JavaScript Bundle: 489.44 kB (gzipped: 128.40 kB)
- Source Map: 2,235.03 kB
