from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = 'secret123'

# ------------------ CLOUDINARY CONFIG ------------------
cloudinary.config(
    cloud_name="dxcb4cs0v",
    api_key="259243188459621",
    api_secret="rcGt0UMCn2pEu-_inyM1bRRDJpg"
)

# ------------------ HOME ------------------
@app.route('/')
def home():
    return render_template('index.html')

# ------------------ REGISTER ------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

# ------------------ LOGIN ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect('/notes')
        else:
            return "Invalid Credentials ❌"

    return render_template('login.html')

# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ------------------ UPLOAD ------------------
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form.get('title')
        subject = request.form.get('subject')
        file = request.files.get('file')

        if file:
            # Upload to Cloudinary
          result = cloudinary.uploader.upload(
    file,
    resource_type="auto",
    type="upload",
    access_mode="public"
)
            file_url = result['secure_url']

            # Save to database
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO notes (title, subject, file_path) VALUES (?, ?, ?)",
                      (title, subject, file_url))
            conn.commit()
            conn.close()

            return redirect('/notes')

    return render_template('upload.html')

# ------------------ NOTES ------------------
@app.route('/notes')
def notes():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM notes")
    data = c.fetchall()
    conn.close()

    return render_template('notes.html', notes=data)

# ------------------ LIVE SEARCH API ------------------
@app.route('/search')
def search():
    query = request.args.get('q', '')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM notes WHERE title LIKE ? OR subject LIKE ?",
              ('%' + query + '%', '%' + query + '%'))

    results = c.fetchall()
    conn.close()

    return {"data": results}

# ------------------ RUN ------------------
if __name__ == '__main__':
    app.run(debug=True)