import random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Create a FastAPI instance
app = FastAPI()

# Initialize Jinja2 template engine
templates = Jinja2Templates(directory="templates")

# Sample list of users for the /list route
users = [
    {"name": "Alice", "age": 30, "email": "alice@example.com"},
    {"name": "Bob", "age": 25, "email": "bob@example.com"},
    {"name": "Charlie", "age": 35, "email": "charlie@example.com"},
    {"name": "David", "age": 40, "email": "david@example.com"},
    {"name": "Eve", "age": 22, "email": "eve@example.com"},
    {"name": "Frank", "age": 29, "email": "frank@example.com"},
]

# Default route (/) - Web GUI
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# /list route - Returns a few random users
@app.get("/list")
async def get_random_users():
    random_users = random.sample(users, 3)  # Select 3 random users
    return random_users

