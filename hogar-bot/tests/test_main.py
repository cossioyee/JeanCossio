from fastapi.testclient import TestClient

import main


def test_health_responde_ok():
    client = TestClient(main.app)
    respuesta = client.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}


def test_lifespan_arranca_y_apaga_en_orden(monkeypatch):
    llamadas = []
    monkeypatch.setattr(main, "create_tables", lambda: llamadas.append("tablas"))
    monkeypatch.setattr(main.migrations, "run", lambda: llamadas.append("migraciones"))
    monkeypatch.setattr(main, "run_seed", lambda: llamadas.append("seed"))
    monkeypatch.setattr(main.scheduler, "setup", lambda: llamadas.append("scheduler"))
    monkeypatch.setattr(main.scheduler, "shutdown", lambda: llamadas.append("apagado"))

    with TestClient(main.app):
        assert llamadas == ["tablas", "migraciones", "seed", "scheduler"]

    assert llamadas[-1] == "apagado"
