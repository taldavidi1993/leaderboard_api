from fastapi.openapi.utils import get_openapi

def add_custom_openapi(app):
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="Leaderboard API",
            version="1.0.0",
            description="API for managing game scores",
            routes=app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "APIKeyHeader": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key"
            }
        }
        openapi_schema["security"] = [{"APIKeyHeader": []}]
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
