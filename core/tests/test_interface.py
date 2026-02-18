import pytest
from fastapi.testclient import TestClient
from click.testing import CliRunner
from core.api.routes import router
from core.cli.main import cli
from fastapi import FastAPI

# --- API Tests ---
app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_api_health():
    response = client.get("/v5/health")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"

def test_api_metrics():
    response = client.get("/v5/metrics")
    assert response.status_code == 200
    assert "vanta_request_total" in response.text

def test_mutation_endpoint():
    payload = {"html": "<div class='test'>Hello</div>"}
    response = client.post("/v5/mutation/preview", json=payload)
    assert response.status_code == 200
    assert "test" not in response.json()["mutated"]  # Class should be renamed

# --- CLI Tests ---
def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Vantablack Core v5" in result.output

def test_cli_setup():
    runner = CliRunner()
    result = runner.invoke(cli, ["setup", "--name", "test_op", "--target", "corp"], input="\n")
    assert result.exit_code == 0
    assert "Initializing campaign" in result.output

def test_cli_mutate_error():
    runner = CliRunner()
    result = runner.invoke(cli, ["mutate", "--file", "nonexistent.html"])
    assert "Error" in result.output
