import os
import webbrowser
import subprocess
import time

# Set the DJANGO_SETTINGS_MODULE environment variable to point to your project's settings.
# Replace 'your_project_name.settings' with the actual path to your project's settings.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EmployeePortal.settings")

def open_browser(url):
    # Open a web browser to the localhost URL
    webbrowser.open(url)

def main():
    # Define the URL
    url = "http://localhost:8000"  # Change the port if your app is running on a different port

    # Start the development server in a separate process
    server_process = subprocess.Popen(["python", "manage.py", "makemigrations"])
    server_process = subprocess.Popen(["python", "manage.py", "migrate"])
    server_process = subprocess.Popen(["python", "manage.py", "runserver"])

    # Wait for a moment to ensure the server has started
    time.sleep(2)  # Adjust the delay as needed

    # Open the web browser
    open_browser(url)

    try:
        # Wait for the server process to complete (Ctrl+C to stop)
        server_process.wait()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
