from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import cloudinary
import cloudinary.uploader
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'noteshub-secret-key-change-in-prod')

# ── Cloudinary (USE ENV VARIABLES IN PRODUCTION) ─────────────
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', 'dxcb4cs0v'),
    api_key=os.environ.get('CLOUDINARY_API_KEY', '259243188459621'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET', 'rcGt0UMCn2pEu-_inyM1bRRDJpg'),
)

DB_PATH = os.environ.get('DB_PATH', 'database.db')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin@noteshub')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── HOME ─────────────────────────────────────────────────────
@app.route('/')
def home():
    conn = get_db()
    total_notes = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    recent = conn.execute("SELECT * FROM notes ORDER BY id DESC LIMIT 4").fetchall()
    conn.close()
    return render_template('index.html', total_notes=total_notes,
                           total_users=total_users, recent=recent)


# ── REGISTER ─────────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if len(username) < 3 or len(password) < 6:
            flash('Username ≥ 3 chars, password ≥ 6 chars.', 'error')
            return render_template('register.html')

        conn = get_db()
        if conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone():
            conn.close()
            flash('Username already taken.', 'error')
            return render_template('register.html')

        conn.execute("INSERT INTO users (username, password) VALUES (?,?)",
                     (username, generate_password_hash(password)))
        conn.commit()
        conn.close()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


# ── LOGIN ─────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = username
            session['user_id'] = user['id']
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('notes'))

        flash('Invalid username or password.', 'error')
    return render_template('login.html')


# ── LOGOUT ───────────────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ── UPLOAD ───────────────────────────────────────────────────
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()
        file = request.files.get('file')

        if not title or not subject:
            flash('Title and subject are required.', 'error')
            return render_template('upload.html')

        if not file or not file.filename:
            flash('Please select a file.', 'error')
            return render_template('upload.html')

        ext = os.path.splitext(file.filename.lower())[1]
        IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}
        VIDEO_EXTS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

        if ext in IMAGE_EXTS:
            resource_type = 'image'
        elif ext in VIDEO_EXTS:
            resource_type = 'video'
        else:
            resource_type = 'raw'

        try:
            result = cloudinary.uploader.upload(
                file,
                resource_type=resource_type,
                folder='noteshub',
                use_filename=True,
                unique_filename=True,
            )

            file_url = result['secure_url']
            original_filename = file.filename

        except Exception as e:
            flash(f'Upload failed: {e}', 'error')
            return render_template('upload.html')

        conn = get_db()
        conn.execute(
            """INSERT INTO notes
               (title, subject, description, file_path, file_type, original_filename, uploaded_by)
               VALUES (?,?,?,?,?,?,?)""",
            (title, subject, description, file_url, resource_type,
             original_filename, session['user'])
        )
        conn.commit()
        conn.close()

        flash('Notes uploaded successfully!', 'success')
        return redirect(url_for('notes'))

    return render_template('upload.html')


# ── NOTES ────────────────────────────────────────────────────
@app.route('/notes')
def notes():
    if 'user' not in session:
        flash('Please log in to view notes.', 'error')
        return redirect(url_for('login'))

    q = request.args.get('q', '').strip()
    subject_filter = request.args.get('subject', '').strip()

    conn = get_db()
    if q:
        data = conn.execute(
            """SELECT * FROM notes
               WHERE title LIKE ? OR subject LIKE ? OR description LIKE ?
               ORDER BY id DESC""",
            (f'%{q}%', f'%{q}%', f'%{q}%')
        ).fetchall()
    elif subject_filter:
        data = conn.execute(
            "SELECT * FROM notes WHERE subject=? ORDER BY id DESC",
            (subject_filter,)
        ).fetchall()
    else:
        data = conn.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()

    subjects = conn.execute(
        "SELECT DISTINCT subject FROM notes ORDER BY subject"
    ).fetchall()
    conn.close()

    return render_template('notes.html', notes=data,
                           subjects=subjects,
                           query=q,
                           subject_filter=subject_filter)


# ── ✅ FIXED VIEW ROUTE ───────────────────────────────────────
@app.route('/view/<int:note_id>')
def view(note_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    note = conn.execute("SELECT file_path FROM notes WHERE id=?", (note_id,)).fetchone()
    conn.close()

    if note:
        return redirect(note['file_path'])  # 🔥 redirect to Cloudinary

    return "File not found", 404


# ── ✅ FIXED DOWNLOAD ROUTE ───────────────────────────────────
@app.route('/download/<int:note_id>')
def download(note_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    note = conn.execute("SELECT file_path FROM notes WHERE id=?", (note_id,)).fetchone()
    conn.close()

    if note:
        # Force download
        return redirect(note['file_path'] + "?fl_attachment=true")

    return "File not found", 404


# ── DELETE ───────────────────────────────────────────────────
@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    note = conn.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()

    if note and note['uploaded_by'] == session['user']:
        conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
        conn.commit()
        flash('Note deleted.', 'success')
    else:
        flash('Permission denied.', 'error')

    conn.close()
    return redirect(url_for('notes'))


# ── ADMIN LOGIN ───────────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Wrong password', 'error')
    return render_template('admin_login.html')


# ── ADMIN DASHBOARD ───────────────────────────────────────────
@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    conn = get_db()
    notes = conn.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()

    return render_template('admin.html', notes=notes, users=users)


# ── RUN ──────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)


