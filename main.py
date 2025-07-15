from fastapi import FastAPI, Request
from auth import verify_api_key
from pydantic import BaseModel, Field
import bisect
import statistics

app = FastAPI()
games_ids={}

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
    users_dic= games_ids[entry.game_id]
    if entry.user_id not in users_dic: #new user_id for this game_id
        users_dic[entry.user_id]={"display_name": entry.display_name, "user_score": entry.user_score}
        return {"message": f"User {entry.user_id} in game {entry.game_id} added successfully"}
    else: #user_id already exists for this game_id
        if users_dic[entry.user_id]["user_score"] < entry.user_score: #update score only if the new score is greater than the old one
            users_dic[entry.user_id]["user_score"] = entry.user_score
            users_dic[entry.user_id]["display_name"] = entry.display_name
            return {"message": f"Score for user {entry.user_id} in game {entry.game_id} updated successfully"}
        else:
            return {"message": f"Score for user {entry.user_id} in game {entry.game_id} not updated, new score is not higher than the old one"}
            

@app.get("/topK/{game_id}") # Define endpoint to get TOPK for a specific game_id
async def get_top_k(game_id: str, request: Request, k: int =3 ): #if k is not provided, default to 3
    #await verify_api_key(request) # block access if API key (need to be for any path)
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


@app.get("/rank/{game_id}/{user_id}") # Define endpoint to rank a specific user in a game
async def get_user_rank(game_id: str, user_id: str, request: Request):    
    #await verify_api_key(request) # block access if API key (need to be for any path)
    if game_id not in games_ids:
        return {"message": f"No scores found for game_id {game_id}"}
    if user_id not in games_ids[game_id]:
        return {"message": f"No score found for user_id {user_id} in game_id {game_id}"}
    score_sorted_list = sorted(games_ids[game_id].items(), key=lambda x: x[1]["user_score"], reverse=True)
    rank = 1
    for idx, (user, data_dict) in enumerate(score_sorted_list):
        if user_id == user:
            return {"message": f"User {user_id} is ranked {rank} in game_id {game_id}",
                    "user_score": data_dict["user_score"],
                    "rank": rank,
                    "percentile": str(round((len(score_sorted_list)-rank / len(score_sorted_list)) * 100, 2))+"%"}
        if idx < len(score_sorted_list) - 1 and data_dict["user_score"] > score_sorted_list[idx+1][1]["user_score"]: #check if the next user has a lower score
            rank += 1

@app.get("/stas/{game_id}") # Define endpoint to get statistics for a specific game_id
async def get_game_statistics(game_id: str, request: Request):
    #await verify_api_key(request) # block access if API key (need to be for any path)
    if game_id not in games_ids:
        return {"message": f"No scores found for game_id {game_id}"}
    total_users = len(games_ids[game_id])
    scores = [user["user_score"] for user in games_ids[game_id].values()] #list comprehension to get all scores
    mean_score = statistics.mean(scores) if scores else 0
    median_score = statistics.median(scores) if scores else 0
    return {
        "message": f"Statistics for game_id {game_id}",
        "total_users": total_users,
        "mean_score":round(mean_score,2), 
        "median_score": round(median_score ,2)
    }