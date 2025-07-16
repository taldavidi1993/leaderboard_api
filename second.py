from fastapi import FastAPI, Request
from auth import verify_api_key
from pydantic import BaseModel, Field
import bisect



app = FastAPI()
games_ids={}
games_ids_rank = {} #to track the rank of the game_id
class ScoreEntry(BaseModel):
    user_id: str
    display_name: str
    game_id: str
    user_score: int =Field(...,gt=0, description="Score must be greater than 0")


@app.get("/") # Define endpoint with a GET request (root path)
def read_root(request: Request):
    #verify_api_key(request)
    return {"message": "Hello, Leaderboard!"}


@app.post("/score/") # Define endpoint for create or update score
async def create_or_update_score(entry: ScoreEntry, request: Request):
    #await verify_api_key(request) # block access if API key (need to be for any path)
    if entry.game_id not in games_ids: #new game_id no one play it before
        games_ids[entry.game_id] = {}
        games_ids[entry.game_id]["score_list"].append(entry.user_score)
        games_ids[entry.game_id]["users"][entry.user_id] = {"display_name" : entry.display_name, "user_score" :entry.user_score, "rank" :1 }
        return {"message": "New game created and score added successfully"}
    else:
        if entry.user_id not in games_ids[entry.game_id]["users"]: #new user_id for this game_id
            index =bisect.bisect_left(games_ids[entry.game_id]["score_list"],entry.user_score)
            games_ids[entry.game_id]["score_list"].insert(index, entry.user_score)
            rank = len(games_ids[entry.game_id]["score_list"]) - index
            for user in games_ids[entry.game_id]["users"]:
                if games_ids[entry.game_id]["users"][user]["rank"] <= rank:
                    games_ids[entry.game_id]["users"][user]["rank"] += 1
            games_ids[entry.game_id]["users"][entry.user_id] = {"display_name" : entry.display_name, "user_score" :entry.user_score, "rank" :rank }
            return {"message": f"User {entry.user_id} in game {entry.game_id} added successfully"}
        else: #user_id already exists for this game_id
            if entry.user_score > games_ids[entry.game_id][entry.user_id].user_score: #update score only if the new score is greater than the old one
                games_ids[entry.game_id][entry.user_id].user_score = entry.user_score
                games_flags[entry.game_id] = False
                #games_id[entry.game_id][entry.user_id].display_name = entry.display_name
                return {"message": f"Score for user {entry.user_id} in game {entry.game_id} updated successfully"}
            else:
                return {"message": f"No update needed for user {entry.user_id} in game {entry.game_id}"}
            

@app.get("/topK/{game_id}") # Define endpoint to get TOPK for a specific game_id
async def get_top_k(game_id: str, request: Request, k: int =3 ): #if k is not provided, default to 3
    #await verify_api_key(request) # block access if API key (need to be for any path)
    if game_id not in games_ids:
        return {"message": f"No scores found for game_id {game_id}"}
    if k<=0 :
        return {"message": f"K must be greater than 0"}
    if k< len(games_ids[game_id]): 
        top_k_scores = sorted_scores_func(game_id)[:k]
        message = f"Top {k} scores for game_id {game_id}"
    else :
        top_k_scores = sorted_scores_func(game_id)
        message = f"Requested K is greater than the number of scores, returning all scores for game_id {game_id}"
    return {
        "message": message ,
        "top_k": [
        {
        "rank": idx + 1,
        "user_id": user.user_id,
        "display_name": user.display_name,
        "user_score": user.user_score
        }
        for idx, user in enumerate(top_k_scores) 
]
}
@app.get("/rank/{game_id}") # Define endpoint to rank a specific user in a game
async def get_user_rank(game_id: str, user_id: str, request: Request):
    #await verify_api_key(request) # block access if API key (need to be for any path)
    if game_id not in games_ids:
        return {"message": f"No scores found for game_id {game_id}"}
    if user_id not in games_ids[game_id]:
        return {"message": f"No score found for user_id {user_id} in game_id {game_id}"}
    sorted_scores = sorted_scores_func(game_id)
    user_rank= sorted_scores.index(games_ids[game_id][user_id]) + 1 #index starts from 0, rank starts from 1
    user_percntile = (user_rank / len(sorted_scores)) * 100
    return {
        "message": f"User {user_id} rank in game {game_id}",
        "user_score": games_ids[game_id][user_id].user_score, 
        "user_rank" : user_rank , #just to make it a string
        "user_percentile": user_percntile +"%"}



def sorted_scores_func(game_id :str):
    if not games_flags[game_id]: #if flag is true, no need to sort again 
        sorted_scores = sorted(games_ids[game_id].values(), key=lambda x: x.user_score, reverse=True) #nlogn sort
        games_flags[game_id] = True #set flag to true after sorting
        return sorted_scores
    else:
        return list(games_ids[game_id].values())
