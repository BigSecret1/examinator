# Examinator

> Train your brain everyday with questions from various subjects & topics.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

## Tech Stack

| Layer    | Technology                       |
| -------- | -------------------------------- |
| Frontend | Next.js 15 (TypeScript)          |
| Backend  | Django 5 + Django REST Framework |
| Database | PostgreSQL 16                    |

## Repository Structure

```
examinator/
├── LICENSE                    # Apache 2.0
├── .gitignore
├── docker-compose.yml         # Full-stack local development
│
├── examinator-web/            # Next.js application
│   ├── public/                # Static assets
│   ├── src/
│   │   ├── app/               # Next.js App Router (pages & layouts)
│   │   ├── components/        # Reusable React components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # API clients, utilities, constants
│   │   ├── styles/            # Global CSS
│   │   └── types/             # Shared TypeScript types
│   ├── next.config.js
│   ├── package.json
│   └── tsconfig.json
│
└── backend/                   # Django REST API
    ├── examinator/            # Django project package
    │   └── settings/
    │       ├── base.py        # Shared settings
    │       ├── development.py # Dev overrides (SQLite)
    │       └── production.py  # Prod overrides (PostgreSQL)
    ├── apps/
    │   ├── users/             # User management & authentication
    │   ├── subjects/          # Subjects & topics
    │   └── questions/         # Questions, answers & quiz logic
    ├── manage.py
    └── requirements.txt
```

## Quick Start (Docker)

```bash
docker compose up --build
```

- Frontend → <http://localhost:3000>
- Backend API → <http://localhost:8000/api/>
- Django Admin → <http://localhost:8000/admin/>

## Local Development

See [examinator-web/README.md](examinator-web/README.md) and [backend/README.md](backend/README.md) for
per-service setup instructions.

## License

Copyright 2026 BigSecret1

Licensed under the [Apache License, Version 2.0](LICENSE).
