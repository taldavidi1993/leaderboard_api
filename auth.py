from fastapi import Request, HTTPException

API_KEY = "my-secret-key" 

async def verify_api_key(request: Request): #checks if the API key is present in the request headers
    api_key = request.headers.get("X-API-Key") # Get the API key from the request headers
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
