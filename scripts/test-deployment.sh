#!/bin/bash

# Deployment Test Script

# Check build
echo "Running build..."
npm run build

# Validate build output
if [ ! -d "dist" ]; then
    echo "Build failed: dist directory not created"
    exit 1
fi

# Check file sizes
CSS_SIZE=$(du -k dist/assets/main-*.css | cut -f1)
JS_SIZE=$(du -k dist/assets/main-*.js | cut -f1)

echo "Build Artifact Sizes:"
echo "CSS: ${CSS_SIZE}KB"
echo "JS: ${JS_SIZE}KB"

# Check for oversized bundles
if [ $JS_SIZE -gt 500 ]; then
    echo "Warning: JavaScript bundle size exceeds 500KB"
fi

# Simulate Firebase deployment dry run
echo "Simulating Firebase deployment..."
firebase hosting:channel:create test-deployment
firebase hosting:channel:deploy test-deployment

# Validate deployment
if [ $? -eq 0 ]; then
    echo "Deployment test successful!"
else
    echo "Deployment test failed"
    exit 1
fi

# Clean up test channel
firebase hosting:channel:delete test-deployment

echo "Deployment test completed successfully!"
