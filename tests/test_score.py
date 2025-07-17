import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
API_KEY = "my-secret-key"
headers = {"X-API-Key": API_KEY}

def test_multiple_games_and_user_behavior():
    from main import games_ids
    games_ids.clear()
    data1 = {"user_id": "u1", "display_name": "Alice", "game_id": "g1", "user_score": 10}
    data2 = {"user_id": "u1", "display_name": "Alice", "game_id": "g2", "user_score": 15}
    resp1 = client.post("/score/", json=data1, headers=headers)
    resp2 = client.post("/score/", json=data2, headers=headers)
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    # Check both games exist in the dictionary and user is present in both
    assert "g1" in games_ids and "g2" in games_ids
    assert "u1" in games_ids["g1"] and "u1" in games_ids["g2"]
    # Check display_name and timestamp for g1
    ts1 = games_ids["g1"]["u1"]["timestamp"]
    assert games_ids["g1"]["u1"]["display_name"] == "Alice"
    # Update score for user in g1 (should update display_name and timestamp)
    data1_update = {"user_id": "u1", "display_name": "Alice2", "game_id": "g1", "user_score": 20}
    resp_update = client.post("/score/", json=data1_update, headers=headers)
    assert resp_update.status_code == 200
    assert "updated successfully" in resp_update.json()["message"]
    assert games_ids["g1"]["u1"]["user_score"] == 20
    assert games_ids["g1"]["u1"]["display_name"] == "Alice2"
    assert games_ids["g1"]["u1"]["timestamp"] > ts1
    # Try to update with a lower score (should not update display_name or timestamp)
    ts2 = games_ids["g1"]["u1"]["timestamp"]
    data1_lower = {"user_id": "u1", "display_name": "Alice3", "game_id": "g1", "user_score": 15}
    resp_lower = client.post("/score/", json=data1_lower, headers=headers)
    assert resp_lower.status_code == 200
    assert "not updated" in resp_lower.json()["message"]
    assert games_ids["g1"]["u1"]["user_score"] == 20
    assert games_ids["g1"]["u1"]["display_name"] == "Alice2"
    assert games_ids["g1"]["u1"]["timestamp"] == ts2
    # Check that user in g2 is unaffected
    assert games_ids["g2"]["u1"]["user_score"] == 15
    assert games_ids["g2"]["u1"]["display_name"] == "Alice"
