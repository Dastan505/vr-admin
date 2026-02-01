# vr-admin

Web-админка календаря VR. Монорепо: backend + frontend + deploy.

## Структура
- `backend/` FastAPI + SQLAlchemy + Alembic
- `frontend/` React + Vite (TypeScript)
- `deploy/` systemd + nginx конфиги

## Локальный запуск (Windows, VS Code)

### 1) Postgres (Docker)
```powershell
docker compose up -d
```

### 2) Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
# отредактируйте .env при необходимости
alembic upgrade head
python -m app.seed.seed_games
python -m app.seed.create_owner --email owner@arena.ru --password ChangeMe123!
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3) Frontend
```powershell
cd ..\frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Открыть: http://localhost:5173

## Деплой на VPS (Linux)

### 1) Размещение
```bash
sudo mkdir -p /opt/vr-admin
sudo chown -R $USER:$USER /opt/vr-admin
cd /opt/vr-admin
# git clone <repo> .
```

### 2) Backend
```bash
cd /opt/vr-admin/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# заполнить DATABASE_URL, JWT_SECRET, CORS_ORIGINS, ADMIN_DEFAULT_LOCATION и т.д.
alembic upgrade head
python -m app.seed.seed_games
python -m app.seed.create_owner --email owner@arena.ru --password ChangeMe123!
```

### 3) Frontend
```bash
cd /opt/vr-admin/frontend
npm install
cp .env.example .env
npm run build
```

### 4) systemd
```bash
sudo cp /opt/vr-admin/deploy/vr-admin-api.service /etc/systemd/system/vr-admin-api.service
sudo systemctl daemon-reload
sudo systemctl enable --now vr-admin-api
```

### 5) Nginx (отдельный домен)
```bash
sudo cp /opt/vr-admin/deploy/nginx-vr-admin.conf /etc/nginx/sites-available/vr-admin.conf
sudo ln -s /etc/nginx/sites-available/vr-admin.conf /etc/nginx/sites-enabled/vr-admin.conf
sudo nginx -t
sudo systemctl reload nginx
```

### Обновления на сервере
```bash
cd /opt/vr-admin
git pull
cd /opt/vr-admin/backend
source .venv/bin/activate
alembic upgrade head
sudo systemctl restart vr-admin-api
cd /opt/vr-admin/frontend
npm install
npm run build
sudo systemctl reload nginx
```

## Переменные окружения

### Backend (`backend/.env`)
```
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/vr_admin
JWT_SECRET=change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:5173,https://admin.arena-api.ru
ADMIN_DEFAULT_LOCATION=Другие Миры — Юго-Восток
DEFAULT_RESOURCE_NAME=Арена 160 м?
```

### Frontend (`frontend/.env`)
```
VITE_API_BASE=/api
```

## Порты
- Backend: `127.0.0.1:8010` (VPS), `127.0.0.1:8000` (локально)
- Frontend: `5173` (Vite dev)
- Postgres: `5432`

## Данные по умолчанию
- Локация: "Другие Миры — Юго-Восток"
- Ресурс: "Арена 160 м?"
- Игры: `backend/app/seed/games.json`
