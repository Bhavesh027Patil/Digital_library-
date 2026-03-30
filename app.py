from flask import Flask, render_template, request, redirect, send_from_directory, session, url_for
import os

# ------------------ CONFIG ------------------
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'secret123'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ------------------ HOME ------------------
@app.route('/')
def home():
    return render_template('index.html')

# ------------------ REGISTER ------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        # You can store in DB here
        return redirect(url_for('login'))
    return render_template('register.html')

# ------------------ LOGIN ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        session['user'] = username
        return redirect(url_for('upload'))
    return render_template('login.html')

# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# ------------------ UPLOAD ------------------
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            return redirect(url_for('notes'))

    return render_template('upload.html')

# ------------------ NOTES ------------------
@app.route('/notes')
def notes():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('notes.html', files=files)

# ------------------ DOWNLOAD ------------------
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ------------------ RUN ------------------
if __name__ == '__main__':
    app.run(debug=True)