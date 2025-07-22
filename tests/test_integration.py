import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
API_KEY = "my-secret-key"
headers = {"X-API-Key": API_KEY}

def test_leaderboard_integration():
    # 1. Add scores for multiple users
    users = [
        {"user_id": "u1", "display_name": "Alice", "game_id": "g1", "user_score": 10},
        {"user_id": "u2", "display_name": "Bob", "game_id": "g1", "user_score": 20},
        {"user_id": "u3", "display_name": "Carol", "game_id": "g1", "user_score": 15},
    ]
    for u in users:
        resp = client.post("/score/", json=u, headers=headers)
        assert resp.status_code == 200
        msg = resp.json()["message"]
        assert "successfully added" in msg or "successfully updated" in msg

    # 2. Update a user's score
    resp = client.post("/score/", json={"user_id": "u1", "display_name": "Alice2", "game_id": "g1", "user_score": 25}, headers=headers)
    assert resp.status_code == 200
    assert "successfully updated" in resp.json()["message"]

    # 3. Get topK
    resp = client.get("/topK/g1?k=2", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["top_k_scores"]) == 2
    assert data["top_k_scores"][0]["user_id"] == "u1"
    assert data["top_k_scores"][1]["user_id"] == "u2"

    # 4. Get rank for a user
    resp = client.get("/rank/g1/u3", headers=headers)
    assert resp.status_code == 200
    rank_data = resp.json()
    assert rank_data["user_rank"] == 3
    assert rank_data["user_score"] == 15
    assert rank_data["display_name"] == "Carol"

    # 5. Get game statistics
    resp = client.get("/stats/g1", headers=headers)
    assert resp.status_code == 200
    stats = resp.json()
    assert stats["total_users"] == 3
    assert stats["mean_score"] == 20.0
    assert stats["median_score"] == 20.0

    # 6. Test error cases
    resp = client.get("/topK/doesnotexist", headers=headers)
    assert resp.status_code == 200
    assert "No scores found" in resp.json()["message"]
    resp = client.get("/rank/g1/notfound", headers=headers)
    assert resp.status_code == 200
    assert "No score found for user_id notfound" in resp.json()["message"]
    resp = client.get("/stats/doesnotexist", headers=headers)
    assert resp.status_code == 200
    assert "No scores found" in resp.json()["message"]

    # 7. Auth required: missing API key
    resp = client.get("/topK/g1?k=2")
    assert resp.status_code == 401
    assert "detail" in resp.json()
