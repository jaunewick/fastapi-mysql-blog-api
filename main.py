from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class BlogBase(BaseModel):
    title: str
    content: str
    user_id: int

class UserBase(BaseModel):
    username: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/blogs", status_code=status.HTTP_201_CREATED)
async def create_blog(blog: BlogBase, db: db_dependency):
    db_blog = models.Blog(**blog.model_dump())
    db.add(db_blog)
    db.commit()

@app.get("/blogs/{blog_id}", status_code=status.HTTP_200_OK)
async def read_blog(blog_id: int, db: db_dependency):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if blog is None:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    return blog

@app.delete("/blog/{blog_id}", status_code=status.HTTP_200_OK)
async def delete_id(blog_id: int, db: db_dependency):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if blog is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    db.delete(blog)
    db.commit()

@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()

@app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user