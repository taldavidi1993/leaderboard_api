# leaderboard_api


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
  curl -X GET "http://localhost:8000/stas/g1" \
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

## Design Decisions

### 1. Data Models
Three Pydantic BaseModel classes are used for clarity and validation:
- **ScoreEntry**: Represents incoming requests. User and game IDs are flexible (string), but can be made stricter if needed.
- **Game**:
    - `users`: Dictionary mapping user IDs to their UserScore objects for efficient lookup and updates.
    - `sort_members`: List of sorted (user_id, UserScore) tuples, generated only when topK or rank queries are made to avoid redundant sorting.
    - `sort_flag`: Boolean tracking whether sorting is needed. Updated whenever a user is added or their score changes.
- **UserScore**: Holds each user's score, display name, and timestamp for fast access and ranking.

### 2. Sorting & Performance
- Sorting is only performed when necessary (topK/rank queries) and cached using `sort_members` and `sort_flag` to avoid repeated sorting.
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
This design optimizes for fast score creation and updates (O(1)), with sorting only performed when needed for topK or rank queries (O(N log N)). Most requests are expected to be score submissions, while ranking queries are less frequent.

- **Score creation/update:** O(1) dictionary lookup and assignment
- **Sorting for topK/rank:** O(N log N), only if the user list was modified since the last sort (tracked by `sort_flag`). Otherwise, O(1) to return cached sorted list.
- **TopK query:** O(K) after sorting
- **Rank query:** O(N) after sorting
- **Game statistics:** O(N) for mean/median calculations

This avoids unnecessary repeated sorting and keeps frequent operations fast. If ranking/topK queries were as frequent as updates, the design could be changed to maintain a sorted list at all times (e.g., using bisect for O(N) insertion), making future queries O(1).

---
## Assumptions or Limitations

- **User ID Uniqueness:** Each user is identified by a unique user ID 
- **Display Name Changes:** Users can change their display name, but it will only update if their score is updated (i.e., only on a successful score change).
- **TOPK :** If k is not provided in a topK request, the default value is 3.
- **Request Frequency  :**It is assumed that create/update score requests are more frequent than topK or rank queries. Therefore, the system is optimized for fast write operations, while read operations perform sorting only when necessary.

---
## 🔗 Live Demo
The API is deployed here:  
👉 [https://leaderboard-api-tth0.onrender.com/docs](https://leaderboard-api-tth0.onrender.com/docs)

Note: All endpoints require `X-API-Key` header.

---

