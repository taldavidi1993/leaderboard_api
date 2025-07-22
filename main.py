from fastapi import FastAPI, Request
from auth import verify_api_key
from pydantic import BaseModel, Field
import statistics
import time
from c_openApi import add_custom_openapi

app = FastAPI()
add_custom_openapi(app)
games={}

class ScoreEntry(BaseModel):
    user_id: str
    display_name: str
    game_id: str
    user_score: int =Field(...,gt=0, description="Score must be greater than 0")

class Game(BaseModel):
    users: dict 
    sort_members: list
    sort_flag: bool

class UserScore(BaseModel):
    display_name: str
    user_score: int
    timestamp: float

@app.get("/") # Define endpoint with a GET request (root path)
async def read_root(request: Request):
    await verify_api_key(request)
    return {"message": "Hello, Leaderboard!"}


@app.post("/score/") # Define endpoint for create or update score
async def create_or_update_score(entry: ScoreEntry, request: Request):
    await verify_api_key(request) # block access  API key
    if entry.game_id not in games: #new game_id: no one play it before
        games[entry.game_id] = Game(users={}, sort_members=[], sort_flag=False)

    users= games[entry.game_id].users
    if entry.user_id not in users: #new user_id for this game_id
        users[entry.user_id]= UserScore(
            display_name=entry.display_name,
            user_score=entry.user_score,
            timestamp=time.time()
        )
        games[entry.game_id].sort_flag = False
        return {"message": f"User {entry.user_id} was successfully added to game {entry.game_id}"}
    
    else: #user_id already exists for this game_id
        if users[entry.user_id].user_score < entry.user_score: #update score only if the new score is greater than the old one
            users[entry.user_id].user_score = entry.user_score
            users[entry.user_id].display_name = entry.display_name
            users[entry.user_id].timestamp = time.time()
            games[entry.game_id].sort_flag = False
            return {"message": f"Score for {entry.user_id} in game {entry.game_id} successfully updated"}
        else:
            return {"message": f"Score for {entry.user_id} in game {entry.game_id} not updated"}
            
def sorting(game_id: str):
    if games[game_id].sort_flag is False: #if the game_id is not sorted, sort it
        games[game_id].sort_members = sorted(
            games[game_id].users.items(),
            key=lambda x: (-x[1].user_score, x[1].timestamp)
        )
        games[game_id].sort_flag = True
    return games[game_id].sort_members

@app.get("/topK/{game_id}") # Define endpoint to get TOPK for a specific game_id
async def get_top_k(game_id: str, request: Request, k: int =3 ): #if k is not provided, default to 3
    await verify_api_key(request) 
    if game_id not in games:
        return {"message": f"No scores found for game_id {game_id}"}
    if k<=0 :
        return {"message": f"K must be greater than 0"}
    score_sorted_list = sorting(game_id) 
    if k >= len(score_sorted_list):
        message = f"Only {len(games[game_id].users)} scores available for game_id {game_id}"
        top_k_scores = score_sorted_list
    else:
        message = f"Top {k} scores for game_id {game_id}"
        top_k_scores = score_sorted_list[:k]
    return {
        "message": message,
        "top_k_scores": [
            {
                "user_id": user_id,
                "display_name": user_data.display_name,
                "user_score": user_data.user_score,
            }
            for user_id, user_data in top_k_scores
        ]
    }


@app.get("/rank/{game_id}/{user_id}") # Define endpoint to rank a specific user in a game
async def get_user_rank(game_id: str, user_id: str, request: Request):    
    await verify_api_key(request)
    if game_id not in games:
        return {"message": f"No scores found for game_id {game_id}"}
    if user_id not in games[game_id].users:
        return {"message": f"No score found for user_id {user_id} in game_id {game_id}"}
    score_sorted_list = sorting(game_id)
    for idx, (usid, user_data) in enumerate(score_sorted_list):
        if user_id == usid:
            return {
                "user_rank": idx + 1,  # rank starts from 1
                "user_score": user_data.user_score,
                "display_name": user_data.display_name,
                "percentile": str(round(((len(score_sorted_list)-(idx + 1))/len(score_sorted_list) )* 100, 2))+"%" 
            }
        
@app.get("/stats/{game_id}") # Define endpoint to get statistics for a specific game_id
async def get_game_statistics(game_id: str, request: Request):
    await verify_api_key(request) 
    if game_id not in games:
        return {"message": f"No scores found for game_id {game_id}"}
    total_users = len(games[game_id].users)
    scores = [user.user_score for user in games[game_id].users.values()] #list comprehension to get all scores
    mean_score = statistics.mean(scores) if scores else 0
    median_score = statistics.median(scores) if scores else 0
    return {
        "message": f"Statistics for game_id {game_id}",
        "total_users": total_users,
        "mean_score": round(mean_score,2), 
        "median_score": round(median_score ,2)
    }