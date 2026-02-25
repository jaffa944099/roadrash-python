#!/bin/bash
# Exit on any error
set -e

BUCKET_NAME=$1

if [ -z "$BUCKET_NAME" ]; then
    echo "Usage: ./publish.sh <gs-bucket-name>"
    echo "Example: ./publish.sh gs://my-app-releases-bucket"
    exit 1
fi

if [ ! -f "dist/LinuxDesktopApp" ]; then
    echo "Executable not found! Please run ./build.sh first."
    exit 1
fi

APP_VERSION=$(date +"%Y%m%d%H%M%S")
ARCHIVE_NAME="LinuxDesktopApp_v${APP_VERSION}.tar.gz"

echo "Creating archive..."
cd dist
tar -czvf ${ARCHIVE_NAME} LinuxDesktopApp
cd ..

echo "Uploading to Google Cloud Storage (${BUCKET_NAME})..."
# Ensure you are authenticated with Google Cloud CLI (gcloud auth login)
gcloud storage cp dist/${ARCHIVE_NAME} ${BUCKET_NAME}/${ARCHIVE_NAME}

echo "Successfully published ${ARCHIVE_NAME} to ${BUCKET_NAME}"
