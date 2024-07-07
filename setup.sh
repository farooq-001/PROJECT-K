# Check package manager and install required system packages
if [ "$PKG_MANAGER" == "apt" ]; then
    sudo apt update
    sudo apt install -y python3-pip python3-venv net-tools
else
    sudo $PKG_MANAGER update
    sudo $PKG_MANAGER install -y python3-pip python3-venv net-tools
fi

# Create and activate virtual environment
python3 -m venv myenv
source myenv/bin/activate

# Install Python packages using pip in the virtual environment
packages=(
    "Flask"
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
    pip install "$package"
done

# Deactivate the virtual environment after installation
deactivate

unzip pycache.zip  && unzip static.zip && unzip templates.zip
rm -rf pycache.zip static.zip  templates.zip
bash run.sh
