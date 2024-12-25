from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List
import uuid

app = FastAPI()

templates = Jinja2Templates(directory="templates")


# Модель пользователя
class User(BaseModel):
    id: int = Field(..., description="Unique identifier for the user")
    username: str = Field(
        ..., min_length=3, max_length=50, description="Username must be between 3 and 50 characters"
    )
    age: int = Field(..., ge=0, le=120, description="Age must be between 0 and 120")


users: List[User] = []


@app.get("/")
async def get_main_page(request: Request):
    """Get Main Page"""
    return templates.TemplateResponse("users.html", {"request": request, "users": users})


@app.get("/user/{user_id}")
async def get_user(request: Request, user_id: int):
    """Get Users"""
    try:
        user = next(user for user in users if user.id == user_id)
        return templates.TemplateResponse("users.html", {"request": request, "user": user})
    except StopIteration:
        raise HTTPException(status_code=404, detail="User not found")


@app.delete("/user/{user_id}")
async def delete_user(user_id: int):
    """Delete User"""
    try:
        user = next(user for user in users if user.id == user_id)
        users.remove(user)
        return {"message": f"User with ID {user_id} has been deleted"}
    except StopIteration:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/user/{username}/{age}")
async def post_user(username: str, age: int):
    """Post User"""
    user_id = len(users) + 1
    user = User(id=user_id, username=username, age=age)
    users.append(user)
    return user


@app.put("/user/{user_id}/{username}/{age}")
async def update_user(user_id: int, username: str, age: int):
    """Update User"""
    try:
        user = next(user for user in users if user.id == user_id)
        user.username = username
        user.age = age
        return user
    except StopIteration:
        raise HTTPException(status_code=404, detail="User not found")


if __name__ == "__main__":
    import uvicorn

    user_index = 1
    new_user = User(id=user_index, username="UrbanUser", age=24)
    users.append(new_user)
    user_index += 1
    new_user = User(id=user_index, username="UrbanTest", age=22)
    users.append(new_user)
    user_index += 1
    new_user = User(id=user_index, username="Capybara", age=60)
    users.append(new_user)

    uvicorn.run(app, host="0.0.0.0", port=8000)