# Leaderboard_api

## 🚀 How to Run Locally

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
2. **Start the server:**
   ```sh
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
3. **Access Swagger UI:**
   - Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

---
## 🔐 Authentication
All API requests require the following header:
```
X-API-Key: my-secret-key
```
---

## 🧪 How to Test the API

### 1. Swagger UI
- Visit [http://localhost:8000/docs](http://localhost:8000/docs)
- Click "Authorize" and enter `my-secret-key` for `X-API-Key`.
- Try out endpoints interactively.

### 2. Postman
- Import the OpenAPI spec from `/docs` or use the endpoints directly.
- Add the header:
  - Key: `X-API-Key`
  - Value: `my-secret-key`
- Example POST request:
  ```json
  POST http://localhost:8000/score/
  Headers: { "X-API-Key": "my-secret-key" }
  Body (JSON):
  {
    "user_id": "u1",
    "display_name": "Alice",
    "game_id": "g1",
    "user_score": 10
  }
  ```

### 3. curl Commands
- **Add/Update Score:**
  ```sh
  curl -X POST "http://localhost:8000/score/" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: my-secret-key" \
    -d '{"user_id": "u1", "display_name": "Alice", "game_id": "g1", "user_score": 10}'
  ```
- **Get Top K:**
  ```sh
  curl -X GET "http://localhost:8000/topK/g1?k=3" \
    -H "X-API-Key: my-secret-key"
  ```
- **Get User Rank:**
  ```sh
  curl -X GET "http://localhost:8000/rank/g1/u1" \
    -H "X-API-Key: my-secret-key"
  ```
- **Get Game Stats:**
  ```sh
  curl -X GET "http://localhost:8000/stats/g1" \
    -H "X-API-Key: my-secret-key"
  ```

### 4. Python Client Example
```python
import requests

API_URL = "http://localhost:8000"
API_KEY = "my-secret-key"
headers = {"X-API-Key": API_KEY}

# Add a score
resp = requests.post(f"{API_URL}/score/", json={
    "user_id": "u1",
    "display_name": "Alice",
    "game_id": "g1",
    "user_score": 10
}, headers=headers)
print(resp.json())

# Get top 3
resp = requests.get(f"{API_URL}/topK/g1?k=3", headers=headers)
print(resp.json())
```

---

## 🛠️ Design Decisions

### 1. Data Models
Three Pydantic BaseModel classes are used for clarity and validation:
- **ScoreEntry**: Represents incoming requests. User and game IDs are flexible (string), but can be made stricter if needed.
- **Game**:
    - `users`: Dictionary mapping user IDs to their UserScore objects for efficient lookup and updates.
    - `sorted_users_cache`: List of sorted (user_id, UserScore) tuples, generated only when topK or rank queries are made to avoid redundant sort_game_score.
    - `is_sorted`: Boolean tracking whether sort_game_score is needed. Updated whenever a user is added or their score changes.
- **UserScore**: Holds each user's score, display name, and timestamp for fast access and ranking.

### 2. Sorting & Performance
- Sorting is only performed when necessary (topK/rank queries) and cached using `sorted_users_cache` and `is_sorted` to avoid repeated sort_game_score.
- Dictionary lookups for users are O(1), making score updates and queries efficient.

### 3. API Security
- All endpoints require an API key via the `X-API-Key` header for authentication.

### 4. Testing
- Comprehensive pytest test suite covers all endpoints, edge cases, and ensures isolation between tests.

### 5. Containerization
- Dockerfile provided for easy deployment and reproducibility.

### 6. Documentation
- Swagger UI is enabled for interactive API exploration and testing.

### 7. Runtime
This design optimizes for fast score creation and updates (O(1)), with sort_game_score only performed when needed for topK or rank queries (O(N log N))

- **Score creation/update:** O(1) dictionary lookup and assignment
- **Sorting for topK/rank:** O(N log N), only if the user list was modified since the last sort (tracked by `is_sorted`). Otherwise, O(1) to return cached sorted list.
- **TopK query:** O(K) after sort_game_score
- **Rank query:** O(N) after sort_game_score
- **Game statistics:** O(N) for mean/median calculations

This avoids unnecessary repeated sort_game_score and keeps frequent operations fast. If ranking/topK queries were as frequent as updates, the design could be changed to maintain a sorted list at all times (e.g., using bisect for O(N) insertion), making future queries O(1).

---
## 📋 Assumptions & Limitations

- **User ID Uniqueness:** Each user is identified by a unique user ID 
- **Display Name Changes:** Users can change their display name, but it will only update if their score is updated (i.e., only on a successful score change).
- **TopK :** If k is not provided in a topK request, the default value is 3.
- **Request Frequency  :** It is assumed that create/update score requests are more frequent than topK or rank queries. Therefore, the system is optimized for fast write operations, while read operations perform sort_game_score only when necessary.
- **User Ranking Decision:** In edge cases where multiple users have the same score, I initially implemented the system to assign them the same rank. However, this led to potential issues when returning the Top K users — it could result in returning more than K users, which might be problematic.
To avoid this, I introduced a secondary ranking criterion: the timestamp of when the score was recorded. In the case of identical scores, the user who achieved the score earlier will be ranked higher. This ensures consistent and fair ordering, especially for Top K queries.

---
## 🤖 Using AI Tools
- **ChatGPT:** Used as a technical reference for Python built-ins, FastAPI patterns, and runtime/data structure questions. Leveraged for validating edge cases and efficiency, but all implementation and design decisions were made independently.
- **GitHub Copilot:** Used for code suggestions, syntax completion, and quick prototyping. All final code was reviewed and customized for clarity, correctness, and project requirements.

---

## 🔗 Live Demo
The API is deployed here:  
👉 [https://leaderboard-api-tth0.onrender.com/docs](https://leaderboard-api-tth0.onrender.com/docs)

Note: All endpoints require `X-API-Key` header.

---

