#!/bin/bash

REPO_NAME="$1"

if [ -z "$REPO_NAME" ]; then
    echo "Error: Repository name not provided"
    exit 1
fi

if [ ! -d "$HOME/.ssh" ]; then
    mkdir -p "$HOME/.ssh"
    echo "Created .ssh directory in home directory"
fi

if ! systemctl --user is-active --quiet podman.socket; then
    echo "Starting podman.socket"
    systemctl --user start podman.socket
fi

if ! systemctl --user is-enabled --quiet podman.socket; then
    echo "Enabling podman.socket"
    systemctl --user enable podman.socket
fi

for VOLUME in "zoxide" "blesh"; do
    VOLUME_NAME="${REPO_NAME}_${VOLUME}"
    if ! podman volume exists "$VOLUME_NAME"; then
        echo "Creating volume: $VOLUME_NAME"
        podman volume create "$VOLUME_NAME"
    fi
done

git config --global core.pager delta
git config --global interactive.diffFilter 'delta --color-only'
git config --global delta.navigate true
git config --global merge.conflictStyle zdiff3