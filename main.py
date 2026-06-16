"""Application entry point."""
from fastapi import FastAPI

from routers import admin, auth, users

# We no longer create tables here via create_all.
# Alembic manages the schema: run `alembic upgrade head` before starting the app.

app = FastAPI(
    title="Auth API",
    description="Learning project: registration, login, JWT, protected endpoints",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Auth API is running. Open /docs"}
