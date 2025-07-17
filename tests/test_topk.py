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

def test_topk_no_k_param():
    # Add 2 users to a new game
    client.post("/score/", json={"user_id": "p1", "display_name": "A", "game_id": "gX", "user_score": 10}, headers=headers)
    client.post("/score/", json={"user_id": "p2", "display_name": "B", "game_id": "gX", "user_score": 20}, headers=headers)
    # No k param, should default to 3
    resp = client.get("/topK/gX", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["top_k_scores"]) == 2  # only 2 users in game
    assert data["top_k_scores"][0]["user_id"] == "p2"
    assert data["top_k_scores"][1]["user_id"] == "p1"

def test_topk_and_rank_changes():
    # Add 4 players
    players = [
        {"user_id": "p1", "display_name": "A", "game_id": "gY", "user_score": 10},
        {"user_id": "p2", "display_name": "B", "game_id": "gY", "user_score": 20},
        {"user_id": "p3", "display_name": "C", "game_id": "gY", "user_score": 15},
        {"user_id": "p4", "display_name": "D", "game_id": "gY", "user_score": 5},
    ]
    for p in players:
        client.post("/score/", json=p, headers=headers)
    ranks = {}
    ranks={"p2": 1, "p3": 2, "p1": 3, "p4": 4}
    resp = client.get("/topK/gY?k=4", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["top_k_scores"]) == 4
    assert data["top_k_scores"][0]["user_id"] == "p2"
    assert data["top_k_scores"][1]["user_id"] == "p3"
    assert data["top_k_scores"][2]["user_id"] == "p1"
    assert data["top_k_scores"][3]["user_id"] == "p4"
    # Change scores
    client.post("/score/", json={"user_id": "p1", "display_name": "A", "game_id": "gY", "user_score": 25}, headers=headers)
    client.post("/score/", json={"user_id": "p4", "display_name": "D", "game_id": "gY", "user_score": 30}, headers=headers)
    # Check new ranks
    resp = client.get("/topK/gY?k=4", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["top_k_scores"]) == 4
    assert data["top_k_scores"][0]["user_id"] == "p4"
    assert data["top_k_scores"][1]["user_id"] == "p1"
    assert data["top_k_scores"][2]["user_id"] == "p2"
    assert data["top_k_scores"][3]["user_id"] == "p3"
    # Make p1 and p4 have the same score
    client.post("/score/", json={"user_id": "p3", "display_name": "A", "game_id": "gY", "user_score": 30}, headers=headers)
    # Now p1 and p4 both have 30
    resp = client.get("/topK/gY?k=4", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    scores = [u["user_score"] for u in data["top_k_scores"]]
    assert scores.count(30) == 2
    user_ids = [u["user_id"] for u in data["top_k_scores"]]
    assert "p3" in user_ids and "p4" in user_ids
    assert len(data["top_k_scores"]) == 4
    assert data["top_k_scores"][0]["user_id"] == "p4"
    assert data["top_k_scores"][1]["user_id"] == "p3"
    assert data["top_k_scores"][2]["user_id"] == "p1"
    assert data["top_k_scores"][3]["user_id"] == "p2"
    # no K param, should return 3 scores by default
    resp = client.get("/topK/gY?", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["top_k_scores"]) == 3  # should return top 3
    
