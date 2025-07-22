import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
API_KEY = "my-secret-key"
headers = {"X-API-Key": API_KEY}

def test_rank_game_not_exist():
    resp = client.get("/rank/doesnotexist/u1", headers=headers)
    assert resp.status_code == 200
    assert "No scores found" in resp.json()["message"]

def test_rank_user_not_in_game():
    client.post("/score/", json={"user_id": "u1", "display_name": "A", "game_id": "gZ", "user_score": 10}, headers=headers)
    resp = client.get("/rank/gZ/notthere", headers=headers)
    assert resp.status_code == 200
    assert "No score found for user_id notthere" in resp.json()["message"]

def test_rank_of_users():
    users = [
        {"user_id": "u1", "display_name": "A", "game_id": "gR", "user_score": 10},
        {"user_id": "u2", "display_name": "B", "game_id": "gR", "user_score": 20},
        {"user_id": "u3", "display_name": "C", "game_id": "gR", "user_score": 15},
    ]
    for u in users:
        client.post("/score/", json=u, headers=headers)
    ranks = {}
    for u in users:
        resp = client.get(f"/rank/gR/{u['user_id']}", headers=headers)
        assert resp.status_code == 200
        ranks[u['user_id']] = resp.json()["user_rank"]
    assert ranks["u2"] == 1
    assert ranks["u3"] == 2
    assert ranks["u1"] == 3

def test_rank_after_score_change():
    client.post("/score/", json={"user_id": "u1", "display_name": "A", "game_id": "gR", "user_score": 25}, headers=headers)
    resp = client.get("/rank/gR/u1", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["user_rank"] == 1
    resp = client.get("/rank/gR/u2", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["user_rank"] == 2

def test_rank_and_topk_match():
    resp = client.get("/topK/gR?k=3", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    topk_ids = [u["user_id"] for u in data["top_k_scores"]]
    users = ["u1", "u2", "u3"]
    ranks = []
    for uid in users:
        r = client.get(f"/rank/gR/{uid}", headers=headers).json()
        ranks.append((r["user_rank"], uid))
    ranks.sort()
    rank_order = [uid for _, uid in ranks]
    assert rank_order == topk_ids

def test_percentile_for_rank_8_of_40():
    for i in range(1, 41):
        client.post(
            "/score/",
            json={"user_id": f"u{i}", "display_name": f"User{i}", "game_id": "gP", "user_score": i},
            headers=headers,
        )
    resp = client.get("/rank/gP/u33", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_rank"] == 8
    assert data["percentile"] == "80.0%"
