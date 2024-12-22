from fastapi import FastAPI, HTTPException, Request, Path
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, validator
from typing import List
import uuid

app = FastAPI()

templates = Jinja2Templates(directory="templates")


# Модель пользователя
class User(BaseModel):
    id: int
    username: str
    age: int

    @validator("username")
    def validate_username(cls, value):
        if not 3 <= len(value) <= 50:
            raise ValueError("Username length must be between 3 and 50 characters")
        return value

    @validator("age")
    def validate_age(cls, value):
        if not 0 <= value <= 120:
            raise ValueError("Age must be between 0 and 120")
        return value


users: List[User] = []
user_id_map = {}


@app.get("/")
async def root(request: Request):
    """Get Main Page"""
    return templates.TemplateResponse("users.html", {"request": request, "users": users})


@app.get("/user/{user_id}")
async def get_user(request: Request, user_id: int):
    """Get Users"""
    user = user_id_map.get(user_id)
    if user:
        return templates.TemplateResponse("users.html", {"request": request, "user": user})
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.delete("/user/{user_id}")
async def delete_user(user_id: int):
    """Delete User"""
    if user_id in user_id_map:
        user = user_id_map.pop(user_id)
        users.remove(user)
        return {"message": f"User with ID {user_id} has been deleted"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.post("/user/{username}/{age}")
async def create_user(username: str, age: int):
    """Post User"""
    user_id = len(user_id_map) + 1
    user = User(id = user_id, username=username, age=age)
    users.append(user)
    user_id_map[user_id] = user
    return user


@app.put("/user/{user_id}/{username}/{age}")
async def update_user(user_id: int, username: str, age: int):
    """Update User"""
    if user_id in user_id_map:
        user = user_id_map[user_id]
        user.username = username
        user.age = age
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


if __name__ == "__main__":
    import uvicorn

    user_index = 1
    new_user = User(id=user_index, username="UrbanUser", age=24)
    users.append(new_user)
    user_id_map[user_index] = new_user
    user_index += 1
    new_user = User(id=user_index, username="UrbanTest", age=22)
    users.append(new_user)
    user_id_map[user_index] = new_user
    user_index += 1
    new_user = User(id=user_index, username="Capybara", age=60)
    users.append(new_user)
    user_id_map[user_index] = new_user

    uvicorn.run(app, host="0.0.0.0", port=8000)