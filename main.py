"""Application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import admin, auth, users

# We no longer create tables here via create_all.
# Alembic manages the schema: run `alembic upgrade head` before starting the app.

app = FastAPI(
    title="Auth API",
    description="Learning project: registration, login, JWT, protected endpoints",
    version="1.0.0",
)

# Allow the React dev server (Vite, port 5173) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Auth API is running. Open /docs"}
