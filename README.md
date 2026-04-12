# NotesHub

A scholarly notes-sharing platform: Flask + SQLite + Cloudinary.

## Project Structure

```
noteshub/
├── app.py               ← Flask routes (home, register, login, upload, notes, admin)
├── database.py          ← DB init + safe migrations
├── requirements.txt
├── database.db          ← SQLite (auto-created)
├── uploads/             ← local temp folder (files go to Cloudinary)
├── static/
│   └── css/
│       └── style.css    ← Full light/dark theme
└── templates/
    ├── base.html        ← Nav, flash messages, theme toggle
    ├── index.html       ← Landing page
    ├── login.html
    ├── register.html
    ├── upload.html
    ├── notes.html       ← Library with View / Download / Delete
    ├── admin_login.html
    └── admin.html       ← Admin dashboard
```

## Quick Start

```bash
pip install -r requirements.txt
python database.py          # create/migrate DB
python app.py               # dev server → http://localhost:5000
```

## Deploy on Render / Railway

Start command: `gunicorn app:app`

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `noteshub-secret-key-change-in-prod` | Flask session secret |
| `CLOUDINARY_CLOUD_NAME` | `dxcb4cs0v` | Cloudinary cloud |
| `CLOUDINARY_API_KEY` | `259243188459621` | Cloudinary key |
| `CLOUDINARY_API_SECRET` | `rcGt0UMCn2pEu-_inyM1bRRDJpg` | Cloudinary secret |
| `ADMIN_PASSWORD` | `admin@noteshub` | Admin portal password |
| `DB_PATH` | `database.db` | SQLite path |

**Set these as env vars in production — never commit secrets.**

## Admin Access

- URL: `/admin/login`  (also linked in homepage footer as "Admin Portal")
- Default password: `admin@noteshub` — **change via `ADMIN_PASSWORD` env var**
- Admin can: view all notes/users, delete any note, delete any user

## View / Download Fix

- **PDFs** → opened in Google Docs Viewer (works everywhere, no plugin needed)
- **Images** → opened in new tab directly  
- **Download** → Cloudinary `fl_attachment` parameter forces browser download

## Features

- ☀️/🌙 Light / Dark mode (persisted via localStorage)
- 🔐 Password hashing (werkzeug)
- 📁 Auto resource-type detection (image / video / raw)
- 🔍 Full-text search + subject filter
- 🗑 Owner-only delete on notes page
- ⚡ Admin delete any note / any user
- 📊 Live stats on homepage
- 📱 Fully responsive