from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import subprocess
from datetime import datetime
import configparser
import psutil
import humanize
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read usernames and passwords from credentials.conf
config = configparser.ConfigParser()
config.read('credentials.conf')
users = dict(config['USERS'])

# Function to get running services
def get_running_services():
    try:
        output = subprocess.check_output(['systemctl', 'list-units', '--type=service', '--state=running']).decode()
        services = []
        for line in output.split('\n')[1:]:
            if line.strip():
                parts = line.split()
                services.append({
                    'service_name': parts[0],
                    'active_pid': parts[1],
                    'status': parts[2],
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        return services
    except subprocess.CalledProcessError as e:
        error_message = f"Error getting running services: {e}"
        logger.error(error_message)
        return []

# Function to get port information
def get_port_information():
    try:
        output = subprocess.check_output(['netstat', '-na']).decode()
        lines = output.split('\n')
        ports = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 4 and parts[0] in ['tcp', 'udp'] and ':' in parts[3]:
                protocol = parts[0]
                local_address = parts[3]
                local_ip, local_port = local_address.split(':')
                remote_address = parts[4] if len(parts) >= 5 else None
                if remote_address:
                    remote_ip, remote_port = remote_address.split(':')
                else:
                    remote_ip, remote_port = None, None
                state = parts[5] if len(parts) >= 6 else ""
                ports.append({
                    'protocol': protocol,
                    'local_ip': local_ip,
                    'local_port': local_port,
                    'remote_ip': remote_ip,
                    'remote_port': remote_port,
                    'state': state
                })
        return ports
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting port information: {e}")
        return []

# Function to execute terminal commands
def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return output.decode()
    except subprocess.CalledProcessError as e:
        error_message = f"Error executing command '{command}': {e.output.decode()}"
        logger.error(error_message)
        return error_message
    except Exception as e:
        error_message = f"Unexpected error executing command '{command}': {str(e)}"
        logger.error(error_message)
        return error_message

# Route to display login page
@app.route('/')
def login_redirect():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            # Store the username in the session
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', title='Login', message='Invalid username or password')
    return render_template('login.html', title='Login')

@app.route('/home')
def home():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', title='Home')

@app.route('/running_services')
def running_services():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    services = get_running_services()
    return render_template('service_info.html', title='Running Services', services=services)

@app.route('/restart/<service_name>', methods=['POST'])
def restart_service(service_name):
    try:
        subprocess.run(['systemctl', 'restart', service_name])
        return redirect(url_for('home'))
    except subprocess.CalledProcessError as e:
        logger.error(f"Error restarting service: {e}")
        return "Error restarting service", 500

# Route to handle logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/resource_information')
def resource_information():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get disk space information
    disk_usage = psutil.disk_usage('/')
    total_disk_space = humanize.naturalsize(disk_usage.total)
    used_disk_space = humanize.naturalsize(disk_usage.used)
    used_disk_space_percent = disk_usage.percent

    # Get memory information
    virtual_memory = psutil.virtual_memory()
    total_memory = humanize.naturalsize(virtual_memory.total)
    used_memory = humanize.naturalsize(virtual_memory.used)
    used_memory_percent = virtual_memory.percent

    # Get uptime information
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())

    return render_template('system_info.html', title='Resource Information', 
                           total_disk_space=total_disk_space, used_disk_space=used_disk_space, 
                           used_disk_space_percent=used_disk_space_percent, total_memory=total_memory, 
                           used_memory=used_memory, used_memory_percent=used_memory_percent, uptime=uptime)

@app.route('/data')
def get_data():
    disk_usage = psutil.disk_usage('/')
    memory_usage = psutil.virtual_memory()

    data = {
        'disk': {
            'total': f"{disk_usage.total / (1024 ** 3):.2f} GB",
            'used': f"{disk_usage.used / (1024 ** 3):.2f} GB",
            'free': f"{disk_usage.free / (1024 ** 3):.2f} GB"
        },
        'memory': {
            'total': f"{memory_usage.total / (1024 ** 3):.2f} GB",
            'used': f"{memory_usage.used / (1024 ** 3):.2f} GB",
            'free': f"{memory_usage.available / (1024 ** 3):.2f} GB"
        }
    }

    return jsonify(data)

@app.route('/port_information')
def port_information():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    port_info = get_port_information()
    return render_template('port_info.html', title='Port Information', port_info=port_info)

# Route to display terminal interface
@app.route('/terminal')
def terminal():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('terminal.html', title='Terminal')

# Route to execute terminal commands
@app.route('/execute_command', methods=['POST'])
def execute_terminal_command():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get command from form
    command = request.form['command']
    
    # Execute the command
    output = execute_command(command)
    
    return render_template('terminal.html', title='Terminal', command=command, output=output)

# Route for the dashboard
@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', title='Dashboard')

if __name__ == '__main__':
    app.run(debug=True)

