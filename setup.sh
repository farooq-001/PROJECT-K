sudo apt update
sudo apt install python3-pip
sudo apt install python3-flask
sudo apt install net-tools
sudo apt update

tee < subprocess.py EOF
import subprocess
# Define the list of packages to install
packages = [
    "Flask",
    "Flask-Login",
    "Flask-WTF",
    "Flask-Bootstrap",
    "Flask-SQLAlchemy",
    "Flask-Migrate",
    "Flask-Admin",
    "Flask-Caching",
    "Flask-Mail",
    "Flask-RESTful",
    "psutil",
    "humanize"
]
# Install the packages using pip
for package in packages:
    subprocess.call(["pip", "install", package])
EOF

/usr/bin/python3   subprocess.py
