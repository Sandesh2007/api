import time
import os
import random
import tempfile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from git import Repo
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REPO_URL = "https://github.com/Sandesh2007/wall_bank"
TEMP_DIR = tempfile.gettempdir()
REPO_DIR = os.path.join(TEMP_DIR, "wallpapers")

# status tracking
server_status = {
    "state": "starting",
    "message": "Server is starting...",
    "last_updated": time.time(),
}


def update_status(state: str, message: str):
    """Update server status."""
    server_status["state"] = state
    server_status["message"] = message
    server_status["last_updated"] = time.time()


@app.get("/", response_class=HTMLResponse)
def read_html():
    """Serve the HTML file at the root."""
    try:
        with open("static/index.html", "r") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading HTML file: {str(e)}")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/status")
def get_status():
    """Get the server status."""
    return {
        "status": server_status["state"],
        "message": server_status["message"],
        "timestamp": server_status["last_updated"],
    }


# supported image extensions
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def clone_or_pull_repo():
    """Clone the repository if it doesn't exist, or pull updates if it does."""
    try:
        if not os.path.exists(REPO_DIR):
            print("Cloning repo...")
            update_status("cloning", "Cloning repository...")
            Repo.clone_from(REPO_URL, REPO_DIR)
            update_status("running", "Repository cloned successfully")
        else:
            print("Pulling repo updates...")
            update_status("pulling", "Pulling latest changes...")
            repo = Repo(REPO_DIR)
            origin = repo.remotes.origin
            origin.pull()
            print("Pulled repo updates")
            update_status("running", "Repository updated successfully")
    except Exception as e:
        update_status("error", f"Repository error: {str(e)}")
        raise


def get_available_categories():
    """Get list of all available categories."""
    categories_path = os.path.join(REPO_DIR, "category")
    if not os.path.exists(categories_path):
        return []

    return [
        d
        for d in os.listdir(categories_path)
        if os.path.isdir(os.path.join(categories_path, d))
    ]


def get_wallpapers_by_category(category: str):
    """Get all wallpapers from a specific category folder."""
    category_path = os.path.join(REPO_DIR, "category", category)
    if not os.path.exists(category_path):
        return None

    wallpapers = [
        os.path.join("category", category, file)
        for file in os.listdir(category_path)
        if any(file.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS)
    ]
    return wallpapers


@app.get("/categories/")
def list_categories():
    """List all available categories."""
    try:
        clone_or_pull_repo()
        categories = get_available_categories()
        return {"categories": categories, "total": len(categories)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-wallpaper/")
def get_wallpaper(category: str = Query("default", description="Category name")):
    """Get a random wallpaper from a specified category."""
    try:
        clone_or_pull_repo()
        available_categories = get_available_categories()
        if category not in available_categories:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f'Category "{category}" not found',
                    "available_categories": available_categories,
                },
            )

        wallpapers = get_wallpapers_by_category(category)
        if not wallpapers:
            raise HTTPException(
                status_code=404,
                detail=f"No wallpapers found in category: {category}",
            )

        random_wallpaper = random.choice(wallpapers)
        filename = os.path.basename(random_wallpaper)
        wallpaper_url = (
            f"https://raw.githubusercontent.com/sandesh2007/wall_bank/master/{random_wallpaper}"
        )

        return {
            "category": category,
            "filename": filename,
            "wallpaper_url": wallpaper_url,
            "total_wallpapers_in_category": len(wallpapers),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/list-wallpapers/")
def list_wallpapers(category: str = Query("default", description="Category name")):
    """List all wallpapers in a given category."""
    try:
        clone_or_pull_repo()
        if category not in get_available_categories():
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f'Category "{category}" not found',
                    "available_categories": get_available_categories(),
                },
            )

        wallpapers = get_wallpapers_by_category(category)
        if not wallpapers:
            raise HTTPException(
                status_code=404,
                detail=f"No wallpapers found in category: {category}",
            )

        return {
            "category": category,
            "wallpapers": [os.path.basename(w) for w in wallpapers],
            "total": len(wallpapers),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)