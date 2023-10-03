from flask import Flask, render_template, request, redirect, url_for
import subprocess
import os

app = Flask(__name__)

# Store the process ID of the running Python script
running_process = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_process():
    global running_process
    if running_process is None:
        # Add the code you want to execute here
        # For example, you can run your Python script using subprocess
        running_process = subprocess.Popen(['python', 'ialert.py'])  # Replace 'a.py' with the actual filename
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop_process():
    global running_process
    if running_process is not None:
        # Terminate the running process
        running_process.terminate()
        running_process = None
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
