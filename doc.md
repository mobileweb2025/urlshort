# shorturl Project Overview

This document explains how the backend, database, and frontend pieces of the short URL project work together. Use it as a quick guide when revisiting the codebase or extending its functionality.

## Project Layout

```
shorturl/                # Project root (git repo)
├── manage.py            # Entry point for Django commands
├── doc.md               # Documentation/architecture guide (this file)
├── .gitignore           # Ignore rules for git
├── links/               # Custom app that handles short URLs
│   ├── admin.py         # Admin registration for ShortLink & PushSubscription
│   ├── apps.py          # App configuration for Django
│   ├── forms.py         # Form + validation for URL input
│   ├── migrations/      # Auto-generated database migrations
│   │   ├── 0001_initial.py   # Creates the ShortLink table
│   │   └── 0002_pushsubscription.py  # Stores push subscription details
│   ├── models.py        # ShortLink + PushSubscription models
│   ├── urls.py          # App-level URL routes
│   ├── utils.py         # Helper functions (send_push_to_all)
│   └── views.py         # Request handlers (home, redirect, offline, subscription API)
├── shorturl/            # Django project settings package
│   ├── settings.py      # Global config (DB, installed apps, templates)
│   ├── urls.py          # Root URL dispatcher
│   ├── asgi.py / wsgi.py   # Entry points for ASGI/WSGI servers
│   └── __init__.py      # Marks the package
├── templates/           # HTML templates for rendering pages
│   ├── base.html        # Shared layout + custom hero/styles + PWA scripts
│   ├── links/home.html  # Main UI for creating/copying short URLs
│   ├── offline.html     # Standalone offline fallback page (PWA)
│   └── sw.js            # Service worker served via Django view
├── static/              # PWA assets (icons, manifest, admin CSS)
│   ├── icons/
│   ├── img/
│   ├── manifest.json
│   └── admin.css
└── db.sqlite3           # Legacy SQLite DB (unused when MySQL is active)
```

> Note: Virtual environments (e.g., `.venv/`) and cache folders (`__pycache__/`) are excluded by `.gitignore`, so they may exist locally without appearing in git.

## 1. Backend Flow

1. **Incoming Request**
   - URLs are defined in `shorturl/urls.py` and `links/urls.py`. A request to `/` goes to `links.views.home`, while `/abc123/` routes to `links.views.redirect_short_link`.

2. **Form Handling**
   - `links/forms.py` defines `ShortLinkForm`, which renders the two inputs shown in the UI (`original_url`, `custom_alias`).
   - Validation logic:
     - Normalizes the custom alias with `slugify`.
     - Ensures the alias has ≥3 characters after normalization.
     - Checks the alias is unique via the ORM (`ShortLink.objects.filter(...)`).
     - Generates a random code when the user leaves the alias blank.

3. **Business Logic in Views**
   - `home()`:
     - Creates the form, validates POST data, and saves a `ShortLink` instance when valid.
     - Uses Django’s message framework to show success/error notifications.
     - Queries the latest 10 `ShortLink` rows to display on the right-hand table.
     - Builds `full_short_url` so the template can show the absolute URL to copy.
   - `redirect_short_link()`:
     - Looks up the `ShortLink` by `short_code`.
     - Increments `click_count` atomically (`F("click_count") + 1`).
     - Redirects the browser to `original_url`.

## 2. Database Layer

1. **Configuration**
   - `shorturl/settings.py` sets `DATABASES['default']` to use MySQL via `mysql.connector.django`, pointing to the `db_shorturl` schema with user/password `root/123456`.
   - `manage.py` and every Django command automatically pick up this configuration, so anytime you run `python manage.py migrate` or `runserver`, Django loads the MySQL connector and connects to `db_shorturl`.
   - Requirements: `mysql-connector-python` must be installed in the virtual environment (see setup steps below) so that Django can import the backend driver.

2. **Schema**
   - `links/models.py` defines the `ShortLink` model (original URL, short code, click counter, timestamps).
   - `python manage.py makemigrations` generated `links/migrations/0001_initial.py`.
   - `python manage.py migrate` created table `links_shortlink` plus Django’s built-in tables (`auth_user`, `django_admin_log`, etc.) inside MySQL.

3. **Data Access**
   - Django ORM automatically translates `.save()`, `.filter()`, `.exists()`, etc. into SQL statements executed against MySQL.
   - You can inspect the data through:
     - Django admin (`/admin/`) after running `python manage.py createsuperuser`.
     - MySQL clients (CLI or GUI such as MySQL Workbench / Sequel Ace) by connecting to `db_shorturl`.

## 3. Frontend Rendering (User Experience)

1. **Base Layout**
   - `templates/base.html` loads the Inter font, custom CSS, PWA scripts, the install button, and the “Enable notifications” button. It also displays flash messages from Django’s message framework. Breakpoints ensure the card feels native on both mobile (full-width) and desktop (≈900px).

2. **Home Page (`templates/links/home.html`)**
   - Extends the base template with a modern single-column card. It renders the form, result box (copy/open buttons), and alias editor. All styles are mobile-first and match the hero.
   - Uses context variables provided by `home()` (`form`, `created_link`, `full_short_url`, `alias_form`, `vapid_public_key`).

3. **Interaction Cycle**
   - User submits the form → browser POSTs to `/`.
   - Django validates input, persists data, and returns a rendered template with the success message + new short link.
   - Clicking the generated short link calls `/short_code/`, which redirects to the original URL while counting the click.

## 4. Typical Workflow to Run Locally

1. Activate virtualenv and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python3 -m pip install django mysql-connector-python
   ```
2. Ensure MySQL has a database named `db_shorturl` and credentials in settings are valid.
3. Apply migrations:
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```
4. (Optional) Create an admin account:
   ```bash
   python3 manage.py createsuperuser
   ```
5. Run the development server and open `http://127.0.0.1:8000/`:
   ```bash
   python3 manage.py runserver
   ```

This sequence wires the backend (Django views + forms + ORM), frontend (templates + custom CSS), and database (MySQL) into a complete short URL service. Use this doc as a reference whenever you need to explain or extend the system.

## 4b. Admin Experience (Jazzmin)

1. **Login Page**
   - Uses Jazzmin theme with a responsive logo (`static/admin.css` ensures it scales on any viewport).
   - Superuser accounts created via `python3 manage.py createsuperuser`.

2. **Dashboard**
   - Jazzmin sidebar exposes “Short links” and “Push subscriptions”.
   - Built-in search/filter forms allow quick lookup by short code, original URL, or endpoint.

3. **ShortLink Management**
   - List view shows `short_code`, `original_url`, `click_count`, timestamps.
   - Detail view lets admin edit target URL or alias, and delete entries.
   - Admin can manually create short links for special campaigns.

4. **PushSubscription Management**
   - `links.models.PushSubscription` is registered so admin can inspect stored subscriptions (endpoint + keys).
   - Useful to monitor how many devices opted in for push notifications.

5. **Extensibility**
   - Additional Jazzmin settings (logo, theme color, nav links) live in `JAZZMIN_SETTINGS`.
   - Future enhancements can expose actions (e.g., reset click counts, trigger push) directly from admin.

## 5. Progressive Web App (PWA) & Push Notifications

1. **Manifest & Icons**
   - `static/manifest.json` registers the app name, start URL, colors, and icons (192px & 512px) generated in `static/icons/`.
   - `<link rel="manifest">`, `<link rel="apple-touch-icon">`, and `<meta name="theme-color">` are set in `templates/base.html`.

2. **Service Worker (`static/sw.js`)**
   - Pre-caches `/`, `/offline/`, manifest, and icons.
   - Provides cache-first strategy for static assets, network-first for pages, and serves `templates/offline.html` when requests fail offline.
   - Handles `push` events to show notifications and `notificationclick` to open the relevant URL.

3. **Install Prompt & Offline Page**
   - Base template registers the service worker and listens for `beforeinstallprompt` to show the “Install app” button.
   - `templates/offline.html` offers a friendly offline message with a retry button.

4. **Push Subscription Pipeline**
   - `links.models.PushSubscription` stores each browser’s endpoint/auth keys.
   - `POST /api/subscriptions/` (`links.views.save_subscription`) records subscriptions (CSRF-protected when accessed via the main page).
   - Frontend JS converts the VAPID public key to a `Uint8Array`, requests notification permission, subscribes via `PushManager`, and posts the subscription to the backend.
   - VAPID keys live in `shorturl/settings.py` (`VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_CLAIMS`). **Regenerate** them for production.

5. **Sending Test Notifications**
   - Use `links.utils.send_push_to_all({"title": "...", "body": "...", "url": "/path"})` from Django shell to broadcast a notification to every stored subscription.
   - For development, push notifications work on `http://localhost:8000`; to test on mobile you must expose the app over HTTPS (e.g., via ngrok).

6. **Testing Checklist**
   - Install PWA on Chrome/Edge desktop or Android via the “Install app” button, or using Safari’s “Add to Home Screen.”
   - Simulate offline in DevTools → Network → Offline, reload, and confirm `offline.html` renders.
   - Click “Enable notifications,” allow the permission prompt, then send a test payload from `send_push_to_all` to verify desktop notifications.

These additions emphasize the “Mobile Web Development” aspect by demonstrating installable, offline-capable behavior plus push notifications powered by Python (Django) and JavaScript.
