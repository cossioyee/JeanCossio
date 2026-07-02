.PHONY: dev test shell db-reset

dev:
	docker compose up --build

test:
	docker compose run --rm bot pytest

shell:
	docker compose run --rm bot /bin/bash

db-reset:
	rm -f data/hogar.db
	docker compose run --rm bot python -c "import os; os.makedirs('data', exist_ok=True); from bot.db.database import create_tables; create_tables()"
	docker compose run --rm bot python -c "from bot.db.seed import run; run()"
