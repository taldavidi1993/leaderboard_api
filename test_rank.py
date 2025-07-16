import pytest
from pydantic import ValidationError
from main import ScoreEntry  
from test_leaderborad_function import create_or_update_score, get_user_rank

games_ids = {}
for i in range(10):
    entry = ScoreEntry(
        user_id=f"user{i}",
        display_name=f"User{i}",
        game_id="game1",
        user_score=i*10 + 10
    )
    create_or_update_score(entry, games_ids)
result =get_user_rank("game1", "user9", games_ids)
assert result["rank"] == 1
entry_update_high = ScoreEntry(
    user_id="user2",
    display_name="User2Updated",
    game_id="game1",
    user_score=999
)
create_or_update_score(entry_update_high, games_ids)
 
result =get_user_rank("game1", "user2", games_ids)
assert result["rank"] == 1
assert games_ids["game1"]["user2"]["user_score"] == 999 
assert games_ids["game1"]["user2"]["display_name"] == "User2Updated"

entry_update_low = ScoreEntry(
    user_id="user2",
    display_name="User2UpdatedLOW",
    game_id="game1",
    user_score=500
)
result =get_user_rank("game1", "user2", games_ids)
assert result["rank"] == 1
assert games_ids["game1"]["user2"]["user_score"] == 999 
assert games_ids["game1"]["user2"]["display_name"] == "User2Updated"

for i in range(10):
    entry = ScoreEntry(
        user_id=f"user{i}",
        display_name=f"User{i}",
        game_id="game1",
        user_score=((i %2) *1000) +1
    )
    create_or_update_score(entry, games_ids)

assert games_ids["game1"]["user0"]["user_score"] == 10
assert games_ids["game1"]["user1"]["user_score"] == 1001
assert games_ids["game1"]["user2"]["user_score"] == 999
assert games_ids["game1"]["user3"]["user_score"] == 1001
assert games_ids["game1"]["user4"]["user_score"] == 50

result =get_user_rank("game1", "user9", games_ids)
assert result["rank"] == 1
assert result["percentile"] == "90.0%"
result= get_user_rank("game1", "user2", games_ids) 
assert result["rank"] == 2
assert result["percentile"] == "80.0%"

for i in range(40):
    entry = ScoreEntry(
        user_id=f"user{i+1}",
        display_name=f"User{i+1}",
        game_id="game2",
        user_score=40-i
    )
    create_or_update_score(entry, games_ids)

assert games_ids["game2"]["user1"]["user_score"] == 40
assert games_ids["game2"]["user8"]["user_score"] == 33
result= get_user_rank("game2", "user8", games_ids) 
assert result["rank"] == 8  
assert result["percentile"] == "80.0%"


