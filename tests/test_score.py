import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
API_KEY = "my-secret-key"
headers = {"X-API-Key": API_KEY}

def test_multiple_games_and_user_behavior():
    from main import games
    games.clear()
    data1 = {"user_id": "u1", "display_name": "Alice", "game_id": "g1", "user_score": 10}
    data2 = {"user_id": "u1", "display_name": "Alice", "game_id": "g2", "user_score": 15}
    resp1 = client.post("/score/", json=data1, headers=headers)
    resp2 = client.post("/score/", json=data2, headers=headers)
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert "g1" in games and "g2" in games
    assert "u1" in games["g1"].users and "u1" in games["g2"].users
    ts1 = games["g1"].users["u1"].timestamp
    assert games["g1"].users["u1"].display_name == "Alice"
    data1_update = {"user_id": "u1", "display_name": "Alice2", "game_id": "g1", "user_score": 20}
    resp_update = client.post("/score/", json=data1_update, headers=headers)
    assert resp_update.status_code == 200
    assert "updated successfully" in resp_update.json()["message"]
    assert games["g1"].users["u1"].user_score == 20
    assert games["g1"].users["u1"].display_name == "Alice2"
    assert games["g1"].users["u1"].timestamp > ts1
    ts2 = games["g1"].users["u1"].timestamp
    data1_lower = {"user_id": "u1", "display_name": "Alice3", "game_id": "g1", "user_score": 15}
    resp_lower = client.post("/score/", json=data1_lower, headers=headers)
    assert resp_lower.status_code == 200
    assert "not updated" in resp_lower.json()["message"]
    assert games["g1"].users["u1"].user_score == 20
    assert games["g1"].users["u1"].display_name == "Alice2"
    assert games["g1"].users["u1"].timestamp == ts2
    assert games["g2"].users["u1"].user_score == 15
    assert games["g2"].users["u1"].display_name == "Alice"
