import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
API_KEY = "my-secret-key"
headers = {"X-API-Key": API_KEY}

def test_invalid_api_key():
    data = {"user_id": "u4", "display_name": "Eve", "game_id": "g1", "user_score": 30}
    bad_headers = {"X-API-Key": "wrong-key"}
    resp = client.post("/score/", json=data, headers=bad_headers)
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Unauthorized"
    
def test_add_new_score():
    data = {"user_id": "u1", "display_name": "Alice", "game_id": "g1", "user_score": 10}
    resp = client.post("/score/", json=data, headers=headers)
    assert resp.status_code == 200
    assert "added successfully" in resp.json()["message"]

def test_update_score_higher():
    data = {"user_id": "u1", "display_name": "Alice", "game_id": "g1", "user_score": 20}
    resp = client.post("/score/", json=data, headers=headers)
    assert resp.status_code == 200
    assert "updated successfully" in resp.json()["message"]

def test_update_score_lower():
    data = {"user_id": "u1", "display_name": "Alice", "game_id": "g1", "user_score": 15}
    resp = client.post("/score/", json=data, headers=headers)
    assert resp.status_code == 200
    assert "not updated" in resp.json()["message"]

def test_top_k_order_and_fields():
    client.post("/score/", json={"user_id": "u2", "display_name": "Bob", "game_id": "g1", "user_score": 18}, headers=headers)
    client.post("/score/", json={"user_id": "u3", "display_name": "Carol", "game_id": "g1", "user_score": 20}, headers=headers)
    resp = client.get("/topK/g1?k=2", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["top_k_scores"]) == 2
    scores = [u["user_score"] for u in data["top_k_scores"]]
    assert scores == sorted(scores, reverse=True)
    for u in data["top_k_scores"]:
        assert "user_id" in u and "display_name" in u and "user_score" in u

def test_rank():
    resp = client.get("/rank/g1/u1", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "user_rank" in data
    assert "user_score" in data
    assert "display_name" in data
    assert "percentile" in data

def test_stats():
    resp = client.get("/stas/g1", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_users" in data
    assert "mean_score" in data
    assert "median_score" in data

def test_invalid_game():
    resp = client.get("/topK/invalidgame", headers=headers)
    assert resp.status_code == 200
    assert "No scores found" in resp.json()["message"]

def test_invalid_k():
    resp = client.get("/topK/g1?k=0", headers=headers)
    assert resp.status_code == 200
    assert "K must be greater than 0" in resp.json()["message"]



