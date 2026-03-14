# Examinator – Backend

This directory contains the **Django** (Python) backend / REST API for the Examinator project.

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

The API will be available at <http://localhost:8000/api/>.

## Folder Structure

```
examinator/          # Django project package (settings, urls, wsgi, asgi)
│   settings/
│   ├── base.py          # Shared settings
│   ├── development.py   # Dev overrides
│   └── production.py    # Prod overrides
apps/
├── users/           # User management & authentication
├── subjects/        # Exam subjects / categories
└── questions/       # Questions, answers, and quiz logic
```

## Running Tests

```bash
pytest
```

## License

Apache 2.0 – see the root [LICENSE](../LICENSE) file for details.
