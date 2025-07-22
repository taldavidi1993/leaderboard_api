import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
API_KEY = "my-secret-key"
headers = {"X-API-Key": API_KEY}

def test_topk_game_not_exist():
    resp = client.get("/topK/doesnotexist", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "No scores found" in data["message"]

def test_topk_invalid_k_type():
    # Try passing a non-integer k (e.g., string)
    resp = client.get("/topK/gX?k=abc", headers=headers)
    assert resp.status_code == 422
    data = resp.json()
    assert "Input should be a valid integer, unable to parse string as an integer" in str(data)

def test_topk_no_k_param():
    client.post("/score/", json={"user_id": "p1", "display_name": "A", "game_id": "gX", "user_score": 10}, headers=headers)
    client.post("/score/", json={"user_id": "p2", "display_name": "B", "game_id": "gX", "user_score": 20}, headers=headers)
    resp = client.get("/topK/gX", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["top_k_scores"]) == 2
    assert data["top_k_scores"][0]["user_id"] == "p2"
    assert data["top_k_scores"][1]["user_id"] == "p1"

def test_topk_and_rank_changes():
    players = [
        {"user_id": "p1", "display_name": "A", "game_id": "gY", "user_score": 10},
        {"user_id": "p2", "display_name": "B", "game_id": "gY", "user_score": 20},
        {"user_id": "p3", "display_name": "C", "game_id": "gY", "user_score": 15},
        {"user_id": "p4", "display_name": "D", "game_id": "gY", "user_score": 5},
    ]
    for p in players:
        client.post("/score/", json=p, headers=headers)
    ranks = {}
    for p in players:
        resp = client.get(f"/rank/gY/{p['user_id']}", headers=headers)
        assert resp.status_code == 200
        ranks[p['user_id']] = resp.json()["user_rank"]
    assert ranks["p2"] == 1
    assert ranks["p3"] == 2
    assert ranks["p1"] == 3
    assert ranks["p4"] == 4
    client.post("/score/", json={"user_id": "p1", "display_name": "A", "game_id": "gY", "user_score": 25}, headers=headers)
    client.post("/score/", json={"user_id": "p4", "display_name": "D", "game_id": "gY", "user_score": 30}, headers=headers)
    ranks = {}
    for p in players:
        resp = client.get(f"/rank/gY/{p['user_id']}", headers=headers)
        assert resp.status_code == 200
        ranks[p['user_id']] = resp.json()["user_rank"]
    assert ranks["p4"] == 1
    assert ranks["p1"] == 2
    assert ranks["p2"] == 3
    assert ranks["p3"] == 4
    client.post("/score/", json={"user_id": "p1", "display_name": "A", "game_id": "gY", "user_score": 30}, headers=headers)
    resp = client.get("/topK/gY?k=4", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    scores = [u["user_score"] for u in data["top_k_scores"]]
    assert scores.count(30) == 2
    user_ids = [u["user_id"] for u in data["top_k_scores"]]
    assert "p1" in user_ids and "p4" in user_ids
    assert len(data["top_k_scores"]) == 4

def test_topk_no_extra_sort():
    # Add 4 users to game gSort
    users = [
        {"user_id": f"u{i}", "display_name": f"User{i}", "game_id": "gSort", "user_score": i*10} for i in range(1, 5)
    ]
    for u in users:
        client.post("/score/", json=u, headers=headers)
    # Request top 4 (should trigger sorting)
    resp4 = client.get("/topK/gSort?k=4", headers=headers)
    assert resp4.status_code == 200
    data4 = resp4.json()
    assert len(data4["top_k_scores"]) == 4
    # Save is_sorted after first sort
    from main import games
    sort_flag_before = games["gSort"].is_sorted
    game_list = games["gSort"].sorted_users_cache
    # Check if game_list is sorted by user_score descending, then timestamp ascending
    is_sorted = game_list == sorted(game_list, key=lambda x: (-x[1].user_score, x[1].timestamp))
    assert is_sorted
    assert sort_flag_before is True
    # Request top 3 (should NOT trigger sorting again)
    resp3 = client.get("/topK/gSort?k=3", headers=headers)
    assert resp3.status_code == 200
    data3 = resp3.json()
    assert len(data3["top_k_scores"]) == 3
    # is_sorted should remain True (no extra sort)
    sort_flag_after = games["gSort"].is_sorted
    assert sort_flag_before is True
    assert sort_flag_after is True

