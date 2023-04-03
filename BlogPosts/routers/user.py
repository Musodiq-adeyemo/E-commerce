from fastapi import APIRouter,Depends,status,UploadFile,File
from BlogPosts.schemas import ShowUser,SchemasUser
from typing import List
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename
from BlogPosts.database import get_db
from BlogPosts.security import oauth2
from BlogPosts.repository import user
from fastapi.templating import Jinja2Templates
from BlogPosts.models import User,UserImage
import shutil

template = Jinja2Templates(directory="templates")


router = APIRouter(
    tags=["Users Information"],
    prefix = "/users"
)

@router.post('/create',response_model=ShowUser, status_code = status.HTTP_201_CREATED,summary="Create User Account")
def create_user(request:SchemasUser,db:Session = Depends(get_db)):
    return user.create_user(request,db)

@router.put('/update/{id}',response_model=ShowUser, status_code = status.HTTP_202_ACCEPTED,summary="Update user information")
def update_post(id,request:SchemasUser,db:Session = Depends(get_db),current_user:SchemasUser = Depends(oauth2.get_current_user)):
    return user.update_user(id,request,db)

@router.delete('/delete/{id}', status_code = status.HTTP_204_NO_CONTENT,summary="Delete user")
def delete_post(id,db:Session = Depends(get_db),current_user:SchemasUser = Depends(oauth2.get_current_user)):
    return user.delete_user(id,db)

@router.get('/{id}',response_model=ShowUser, status_code = status.HTTP_200_OK,summary="Get User by Id")
def get_user(id,db:Session = Depends(get_db),current_user:SchemasUser = Depends(oauth2.get_current_user)):
    return user.get_user(id,db)

@router.get('/get/users',response_model=List[ShowUser], status_code = status.HTTP_200_OK,summary="Get All Users")
def get_all_user(db:Session = Depends(get_db),current_user:SchemasUser = Depends(oauth2.get_current_user)):
    return user.get_all_user(db)

@router.get('/{username}',response_model=ShowUser, status_code = status.HTTP_200_OK,summary="Get User by Username")
def get_username(username:str,db:Session = Depends(get_db),current_user:SchemasUser = Depends(oauth2.get_current_user)):
    return user.get_username(username,db)

@router.post("/upload",summary="Upload your profile picture")
def upload(user_id:int,db:Session = Depends(get_db),file:UploadFile = File(...),current_user:SchemasUser = Depends(oauth2.get_current_user)):
    with open(f"BlogPosts/static/userimages/{file.filename}","wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    name = secure_filename(file.filename)
    mimetype = file.content_type
    user_upload = UserImage(minetype=mimetype,name=name,user_id=user_id)
    db.add(user_upload)
    db.commit()
    return f"{name} has been Successfully Uploaded"