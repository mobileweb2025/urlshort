# ShortURL – Progressive Web Short-Link Generator (Django + PWA)

ShortURL is a Django + MySQL application for creating memorable short links with optional custom aliases. The project ships with a polished user experience, Jazzmin-powered admin dashboard, and full Progressive Web App (PWA) capabilities (installable, offline-ready, and push-notification enabled).

![Frontend screenshot](docs/images/frontend.png "ShortURL form")  
![Admin login screenshot](docs/images/admin-login.png "Jazzmin login")

> Replace the image paths above with the actual location of your screenshots (e.g., `docs/images/...`).  
> This project was built for **Mobile Web Development with Python and JavaScript** (Ismail Khalil).

---

## ✨ Features

- **Modern UI** – Responsive hero + card layout with copy/open buttons and alias editor.
- **Custom aliases** – Users can supply their own slug; system generates a unique fallback.
- **Realtime history** – Recent short links and click counters available through the admin.
- **Jazzmin admin** – Branded, responsive login plus full CRUD on short links and push subscriptions.
- **PWA ready** – Manifest, service worker, offline fallback page, “Install app” prompt.
- **Push notifications** – Users can opt in; developers can broadcast via `send_push_to_all`.
- **MySQL persistence** – Designed for relational storage; compatible with MySQL Workbench, Sequel Ace, etc.

---

## 🧰 Tech Stack

- **Backend:** Django 5, mysql-connector-python, pywebpush, Jazzmin.
- **Frontend:** Django templates, custom CSS (Inter font), service worker + manifest.
- **Database:** MySQL 8 (local) or compatible server.
- **Tooling:** virtualenv, pip, MySQL Workbench (optional).

---

## ✅ Prerequisites

| Requirement            | Notes                                                                 |
|------------------------|-----------------------------------------------------------------------|
| Python 3.11+           | Install from python.org or pyenv                                      |
| MySQL Server           | Must be running locally (`mysql.server start`)                        |
| virtualenv / venv      | For isolated Python packages                                          |
| pip                    | Comes with Python; used to install dependencies                      |
| (Optional) Workbench   | GUI for inspecting MySQL data                                         |

---

## 🚀 Getting Started

1. **Clone & enter the repo**
   ```bash
   git clone https://github.com/<your-user>/shorturl.git
   cd shorturl
   ```

2. **Create + activate a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   python3 -m pip install -r requirements.txt
   ```
   > If `requirements.txt` is not generated yet, install manually:  
   `python3 -m pip install django mysql-connector-python pywebpush jazzmin`

4. **Configure MySQL**
   - Create database `db_shorturl`.
   - Update `shorturl/settings.py` → `DATABASES['default']` if credentials differ.

5. **Run migrations + create superuser**
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   python3 manage.py createsuperuser
   ```

6. **Launch the dev server**
   ```bash
   python3 manage.py runserver 0.0.0.0:8000
   ```
   Visit `http://localhost:8000/` for the frontend and `http://localhost:8000/admin/` for Jazzmin.

---

## 🗂 Project Structure (excerpt)

```
shorturl/
├── links/
│   ├── models.py          # ShortLink + PushSubscription
│   ├── forms.py           # ShortLinkForm
│   ├── views.py           # home, redirect, offline, API
│   ├── utils.py           # send_push_to_all helper
│   └── migrations/
│       ├── 0001_initial.py
│       └── 0002_pushsubscription.py
├── shorturl/
│   ├── settings.py        # DB config, VAPID keys, Jazzmin settings
│   ├── urls.py            # Root routes + service worker
│   └── ...
├── templates/
│   ├── base.html          # Shared layout + install/push controls
│   ├── links/home.html
│   ├── offline.html       # Offline fallback
│   └── sw.js              # Served service worker
├── static/
│   ├── icons/
│   ├── img/logo.png
│   ├── manifest.json
│   └── admin.css          # Responsive Jazzmin logo
└── doc.md                 # Full architecture guide
```

---

## 📱 PWA & Push Notifications

1. **Manifest & Icons**  
   Already configured in `static/manifest.json` + `<head>` tags.

2. **Installation**  
   - Open Chrome/Edge → `http://localhost:8000/` → click **Install app**.
   - Safari (iOS/macOS) → Share → “Add to Home Screen”.

3. **Offline Support**  
   - DevTools → Network → Offline → reload → offline page (`offline.html`) appears.

4. **Enable Notifications**  
   - Click **Enable notifications** → Allow permission.
   - Works on `http://localhost` (Chrome desktop). For LAN/mobile, expose via HTTPS (e.g., ngrok).

5. **Send a test push**
   ```bash
   python3 manage.py shell
   >>> from links.utils import send_push_to_all
   >>> send_push_to_all({"title": "ShortURL", "body": "Test push", "url": "/"})
   ```
   > Ensure MySQL is running and browser tab is open.

---

## 🔐 Admin (Jazzmin)

- Login: `http://localhost:8000/admin/` (use superuser credentials).
- Features:
  - View/search/edit short links and click counts.
  - Inspect push subscriptions to see who opted in.
  - Jazzmin customizations (`JAZZMIN_SETTINGS`) handle branding + responsive logo.
- Screenshot:
  ```
  docs/images/admin-login.png
  ```

---

## 🧪 Troubleshooting

| Issue                                   | Fix                                                                                   |
|-----------------------------------------|----------------------------------------------------------------------------------------|
| `ModuleNotFoundError: django`           | Ensure virtualenv is activated before running commands.                               |
| MySQL `2003 (HY000)` connection error   | Start MySQL (`mysql.server start`) and confirm credentials in `settings.py`.          |
| Notifications stuck on “Enabling…”      | Use `http://localhost:8000/` (secure context) and check DevTools → Console/Network.    |
| Offline page not shown                  | Clear service worker cache (DevTools → Application → Clear storage → Unregister).     |
| Push not reaching device                | Make sure browser tab is open and permission is granted; trigger via shell helper.    |

---

## 📄 License

Specify your license here (e.g., MIT). Replace this section with actual terms before publishing.

---

## 🙌 Acknowledgements

- Django + Jazzmin for rapid admin UI.
- pywebpush + Chrome DevTools for PWA debugging.
- Built as an example project for **Mobile Web Development with Python and JavaScript — Ismail Khalil**.

Happy shortening! 🚀
