#!/bin/bash

# Determine the package manager
if command -v dnf >/dev/null 2>&1; then
    PKG_MANAGER="dnf"
elif command -v yum >/dev/null 2>&1; then
    PKG_MANAGER="yum"
elif command -v apt >/dev/null 2>&1; then
    PKG_MANAGER="apt"
else
    echo "Unsupported distribution"
    exit 1
fi

# Update package lists
if [ "$PKG_MANAGER" == "apt" ]; then
    sudo apt update
else
    sudo $PKG_MANAGER update -y
fi

# Install Python 3, pip, Flask, and net-tools
if [ "$PKG_MANAGER" == "apt" ]; then
    sudo apt install -y python3-pip python3-flask net-tools
else
    sudo $PKG_MANAGER install -y python3-pip python3-flask net-tools
fi

# Install other packages using pip
packages=(
    "Flask-Login"
    "Flask-WTF"
    "Flask-Bootstrap"
    "Flask-SQLAlchemy"
    "Flask-Migrate"
    "Flask-Admin"
    "Flask-Caching"
    "Flask-Mail"
    "Flask-RESTful"
    "psutil"
    "humanize"
)

for package in "${packages[@]}"; do
    sudo -H pip3 install "$package"
done
