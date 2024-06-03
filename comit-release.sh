#!/bin/bash

# Prompt user for information
read -p "Enter your GitHub token: " GITHUB_TOKEN

read -p "Enter the repository name (e.g., username/repo): " REPO_NAME

#read -p "Enter the release name: " RELEASE_NAME

#BRANCH_NAME="prefix-downloads"
read -p "Enter the branch to release from (e.g., main, prefix-downloads): " BRANCH_NAME


# Define constants
DIRECTORY="/home/$USER/.steam/steam/steamapps/compatdata/prefixes"
API_URL="https://api.github.com/repos/$REPO_NAME/releases"
TAGS_URL="https://api.github.com/repos/$REPO_NAME/git/refs"

# Check if there are any .zip files in the directory
if ! ls "$DIRECTORY"/*.zip >/dev/null 2>&1; then
    echo "No .zip files found in the directory. Please specify a custom file path."
    read -p "Enter the full path to your file: " FILE_PATH
else
    # List files and ask for user input or custom path
    echo "Select a file from the list below or enter 'custom' to specify a path:"
    select FILE_CHOICE in $(ls "$DIRECTORY"/*.zip) "custom"
    do
        if [ "$FILE_CHOICE" = "custom" ]; then
            read -p "Enter the full path to your file: " FILE_PATH
        else
            FILE_PATH=$FILE_CHOICE
        fi
        break
    done
fi

if [[ ! -f "$FILE_PATH" ]]
then
    echo "Missing file: $FILE_PATH"
    exit 1
fi

# Extract version from filename
VERSION_NAME=$(echo "$FILE_PATH" | grep -oP 'GE-Proton\K[\d.]+(?=.zip)')
if [[ -z "$VERSION_NAME" ]]; then
    read -p "Enter the version for the release: " VERSION_NAME
fi

# Construct the tag name
TAG_NAME="PfxVer$VERSION_NAME"

if [[ ! -z "$RELEASE_NAME" ]]
then
    RELEASE_NAME="Prefix GE-Proton$VERSION_NAME $RELEASE_NAME"
else
    RELEASE_NAME="Prefix GE-Proton$VERSION_NAME"
fi

FILE_NAME=$(basename "$FILE_PATH")

RELEASE_DESCRIPTION="This is the download for a WeMod ready GE-Proton$VERSION_NAME prefix.  
**If you want to download the WeMod Launcher check the guide.**  
`The WeMod Launcher will auto download this prefix if needed.`"

echo ""
echo "API_URL: $API_URL"
echo "TAG_NAME: $TAG_NAME"
echo "RELEASE_NAME: $RELEASE_NAME"
echo "FILE_PATH: $FILE_PATH"
echo "FILE_NAME: $FILE_NAME"
echo "BRANCH_NAME: $BRANCH_NAME"
echo "RELEASE_DESCRIPTION: $RELEASE_DESCRIPTION"
echo ""


read -p "Press enter to create release and upload"

echo ""
echo "Chcking if the tag already exists"

# Check if the tag already exists
if curl -s -H "Authorization: token $GITHUB_TOKEN" "$TAGS_URL/tags/$TAG_NAME" | grep -q '"ref":'; then
    echo "Tag $TAG_NAME already exists."
    exit 1
fi

# Fetch the latest commit SHA from the specified branch
LATEST_COMMIT_SHA=$(git rev-parse "$BRANCH_NAME")

echo ""

# Create a tag and release based on specific branch
echo "Creating tag $TAG_NAME for branch $BRANCH_NAME with sha $LATEST_COMMIT_SHA..."
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
     -H "Content-Type: application/json" \
     -d "{\"ref\": \"refs/tags/$TAG_NAME\", \"sha\": \"$LATEST_COMMIT_SHA\"}" \
     "$TAGS_URL"

echo ""

# Create the release
echo "Creating release $RELEASE_NAME at $TAG_NAME..."
RELEASE_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
                         -H "Content-Type: application/json" \
                         -d "{\"tag_name\": \"$TAG_NAME\", \"name\": \"$RELEASE_NAME\", \"body\": \"$RELEASE_DESCRIPTION\", \"draft\": false, \"prerelease\": false}" \
                         $API_URL)

# Extract the upload URL from the release response
UPLOAD_URL=$(echo $RELEASE_RESPONSE | grep -oP '"upload_url": "\K[^"{]+')

# Modify the upload URL for asset upload
UPLOAD_URL=${UPLOAD_URL%\{*}?name="$FILE_NAME"

echo "Printing release response..."
echo "$RELEASE_RESPONSE"
echo ""

# Upload the file
echo "Uploading $FILE_PATH to $UPLOAD_URL..."
echo ""
curl -H "Authorization: token $GITHUB_TOKEN" \
     -H "Content-Type: application/octet-stream" \
     --data-binary @"$FILE_PATH" \
     "$UPLOAD_URL"

echo ""
echo ""
echo "File uploaded successfully."
