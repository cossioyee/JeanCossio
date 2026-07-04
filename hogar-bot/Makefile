.PHONY: dev test shell db-reset

dev:
	docker compose up --build

test:
	docker compose run --rm bot pytest --cov=bot --cov=main --cov-report=term-missing --cov-fail-under=80

shell:
	docker compose run --rm bot /bin/bash

db-reset:
	rm -f data/hogar.db data/hogar.db-shm data/hogar.db-wal
	docker compose run --rm bot python -c "import os; os.makedirs('data', exist_ok=True); from bot.db.database import create_tables; create_tables()"
	docker compose run --rm bot python -c "from bot.db.seed import run; run()"
