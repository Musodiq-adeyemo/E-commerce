from fastapi import APIRouter,Depends,UploadFile,File,status
from BlogPosts.schemas import ShowStore,SchemasUser,CreateStore
from typing import List
from sqlalchemy.orm import Session
from BlogPosts.database import get_db
from BlogPosts.security.oauth2 import get_current_user
from BlogPosts.repository import store
from BlogPosts.models import Store
import shutil
from BlogPosts.security import oauth2



router = APIRouter(
    tags=["STORE"],
    prefix = "/stores"
)


@router.get('',response_model= List[ShowStore],summary="Get all Store")
def show_store(db:Session = Depends(get_db),current_user:SchemasUser = Depends(get_current_user)):
    return store.show_store(db)

@router.get('/{id}',response_model= ShowStore,summary="Get Store by Id")
def show_store_id(id:int,db:Session = Depends(get_db),current_user:SchemasUser = Depends(get_current_user)):
    return store.show_store_id(id,db)

@router.get('/{name}',response_model= ShowStore,summary="Get Store by Name")
def show_store_name(name:str,db:Session = Depends(get_db),current_user:SchemasUser = Depends(get_current_user)):
    return store.show_store_name(name,db)

@router.post('/create', response_model=ShowStore,status_code = status.HTTP_201_CREATED,summary="Create a Store")
def create_store(request:CreateStore,db:Session = Depends(get_db),current_user:SchemasUser = Depends(get_current_user)):
    return store.create_store(request,db)

@router.put('/update/{id}',response_model=ShowStore, status_code = status.HTTP_202_ACCEPTED,summary="Update Your Store")
def update_store(id,request:ShowStore,db:Session = Depends(get_db),current_user:SchemasUser = Depends(get_current_user)):
    return store.update_store(id,request,db)

@router.delete('/delete/{id}', status_code = status.HTTP_204_NO_CONTENT,summary="Delete Store")
def delete_store(id,db:Session = Depends(get_db),current_user:SchemasUser = Depends(get_current_user)):
    return store.delete_store(id,db)

