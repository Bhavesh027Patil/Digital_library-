from flask import Flask, render_template, request, redirect, send_from_directory, session
import sqlite3
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'secret123'   # 🔐 Required for session


# -------------------- FILE DOWNLOAD --------------------
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


# -------------------- HOME --------------------
@app.route('/')
def home():
    return render_template('index.html')


# -------------------- REGISTER --------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')


# -------------------- LOGIN --------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = username   # ✅ store user session
            return redirect('/notes')
        else:
            return "Invalid Credentials ❌"

    return render_template('login.html')


# -------------------- LOGOUT --------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


# -------------------- VIEW NOTES (WITH SEARCH + PROTECTION) --------------------
@app.route('/notes')
def notes():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    search_query = request.args.get('search')

    if search_query:
        c.execute("SELECT * FROM notes WHERE title LIKE ? OR subject LIKE ?", 
                  ('%' + search_query + '%', '%' + search_query + '%'))
    else:
        c.execute("SELECT * FROM notes")

    data = c.fetchall()
    conn.close()

    return render_template('notes.html', notes=data)


# -------------------- ADMIN LOGIN --------------------
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin':
            return redirect('/admin')
        else:
            return "Invalid Admin Credentials ❌"

    return render_template('admin_login.html')


# -------------------- ADMIN PANEL --------------------
@app.route('/admin')
def admin():
    return render_template('admin.html')


# -------------------- UPLOAD NOTES --------------------
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        subject = request.form['subject']
        file = request.files['file']

        filename = file.filename

        # Save file
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Save to DB (only filename)
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO notes (title, subject, file_path) VALUES (?, ?, ?)",
                  (title, subject, filename))
        conn.commit()
        conn.close()

        return redirect('/notes')

    return render_template('upload.html')


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



# -------------------- RUN APP --------------------
if __name__ == '__main__':
    app.run(debug=True)