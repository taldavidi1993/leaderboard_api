import pytest
from pydantic import ValidationError
from main import ScoreEntry  
from test_data_entries import entries

def test_score_entry_invalid_score():
    with pytest.raises(ValidationError) as exc_info:
        ScoreEntry(
            user_id="user1",
            display_name="Alice",
            game_id="game1",
            user_score=-5
        )

    assert "greater than 0" in str(exc_info.value)

def test_update_score():
    games_ids = {}
    for entry in entries:
        if entry.game_id not in games_ids: #new game_id no one play it before
            games_ids[entry.game_id] = {}
        users_dic= games_ids[entry.game_id]
        if entry.user_id not in users_dic: #new user_id for this game_id
            users_dic[entry.user_id]={"display_name": entry.display_name, "user_score": entry.user_score}
        else: #user_id already exists for this game_id
            if users_dic[entry.user_id]["user_score"] < entry.user_score: #update score only if the new score is greater than the old one
                users_dic[entry.user_id]["user_score"] = entry.user_score
                users_dic[entry.user_id]["display_name"] = entry.display_name
    assert games_ids == {
        "game1": {
            "user1": {"display_name": "AliceTheQueen", "user_score": 100},
            "user2": {"display_name": "Bob", "user_score": 100},
        },
        "game2": {
            "user2": {"display_name": "Bob", "user_score": 100},
        }
    }   

def get_top_k(game_id, k, games_ids):     
    if game_id not in games_ids:
        return {"message": f"No scores found for game_id {game_id}"}
    if k<=0 :
        return {"message": f"K must be greater than 0"}
    score_sorted_list = sorted(games_ids[game_id].items(), key=lambda x: x[1]["user_score"], reverse=True)
    if k >= len(games_ids[game_id]):
        message = f"Only {len(games_ids[game_id])} scores available for game_id {game_id}"
        top_k_scores = score_sorted_list
    else:
        k_score = score_sorted_list[k-1][1]["user_score"] #to handle the case where multiple users have the same score as the Kth rank
        top_k_scores =score_sorted_list[:k] #the list is already sorted, so we can take the first k elements
        # Now we need to check if there are more users with the same score
        for user in score_sorted_list[k:]:
            if user[1]["user_score"] == k_score: # Let's play fair: include all users who share the same score as the Kth rank
                top_k_scores.append(user)
            else:
                break # stop when we find a user with a lower score(this is because the list is sorted in descending order)
        if k< len(top_k_scores):
            message = f"More than {k} users are returned because multiple users share the same score"
        else:
            message = f"Top {k} scores for game_id {game_id}"
    return {"message": message,
            "k_requested": k,
            "returned_users": len(top_k_scores),
            "top_K_scores": [
            {
                "user_id": user_id,
                "display_name": user_data["display_name"],
                "user_score": user_data["user_score"]
            }
            for user_id, user_data in top_k_scores
        ]
}   
def test_game_id_not_found():
    result = get_top_k("game999", 3, {})
    assert result["message"] == "No scores found for game_id game999"

def test_game_id_not_found():
    result = get_top_k("game999", 3, {})
    assert result["message"] == "No scores found for game_id game999"
def test_k_bigger_than_users():
    games_ids = {
        "game1": {
            "user1": {"display_name": "Alice", "user_score": 100},
            "user2": {"display_name": "Bob", "user_score": 90},
        }
    }
    result = get_top_k("game1", 10, games_ids)
    assert result["message"] == "Only 2 scores available for game_id game1"
    assert result["returned_users"] == 2

def test_fair_game_extra_users():
    games_ids = {
        "game1": {
            "user1": {"display_name": "Alice", "user_score": 100},
            "user2": {"display_name": "Bob", "user_score": 90},
            "user3": {"display_name": "Charlie", "user_score": 80},
            "user4": {"display_name": "Dana", "user_score": 80},
        }
    }
    result = get_top_k("game1", 3, games_ids)
    assert result["message"].startswith("More than 3 users are returned")
    assert result["returned_users"] == 4

