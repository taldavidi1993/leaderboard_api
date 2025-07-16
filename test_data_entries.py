from main import ScoreEntry

entry_1 = ScoreEntry(
    user_id="user1",
    display_name="Alice",
    game_id="game1",
    user_score=50
)

entry_2 = ScoreEntry(
    user_id="user1",
    display_name="AliceTheQueen",
    game_id="game1",
    user_score=100
)

entry_3 = ScoreEntry(
    user_id="user2",
    display_name="Bob",
    game_id="game1",
    user_score=100
)

entry_4 = ScoreEntry(
    user_id="user2",
    display_name="Bob",
    game_id="game2",
    user_score=100
)

entry_5 = ScoreEntry(
    user_id="user2",
    display_name="Bob",
    game_id="game2",
    user_score=50
)

entries = [entry_1, entry_2, entry_3, entry_4, entry_5]
