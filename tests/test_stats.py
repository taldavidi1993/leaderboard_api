import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
API_KEY = "my-secret-key"
headers = {"X-API-Key": API_KEY}

def test_stats_game_not_exist():
    resp = client.get("/stats/doesnotexist", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "No scores found" in data["message"]

def test_stats_five_users():
    users = [
        {"user_id": "u1", "display_name": "A", "game_id": "gS", "user_score": 10},
        {"user_id": "u2", "display_name": "B", "game_id": "gS", "user_score": 20},
        {"user_id": "u3", "display_name": "C", "game_id": "gS", "user_score": 30},
        {"user_id": "u4", "display_name": "D", "game_id": "gS", "user_score": 40},
        {"user_id": "u5", "display_name": "E", "game_id": "gS", "user_score": 50},
    ]
    for u in users:
        client.post("/score/", json=u, headers=headers)
    resp = client.get("/stats/gS", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_users"] == 5
    assert data["mean_score"] == 30.0
    assert data["median_score"] == 30.0

def test_stats_update_and_add_user():
    client.post("/score/", json={"user_id": "u1", "display_name": "A", "game_id": "gS", "user_score": 60}, headers=headers)
    client.post("/score/", json={"user_id": "u6", "display_name": "F", "game_id": "gS", "user_score": 25}, headers=headers)
    resp = client.get("/stats/gS", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_users"] == 6
    assert data["mean_score"] == 37.5
    assert data["median_score"] == 35.0


