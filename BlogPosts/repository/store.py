from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from BlogPosts.models import Store
from BlogPosts.schemas import CreateStore
from typing import List


def show_store(db:Session):
    stores = db.query(Store).all()
    return stores

def show_store_id(id:int,db:Session):
    store = db.query(Store).filter(Store.id==id).first()
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Store with id {id} not found")
    
    return store

def show_store_name(name:int,db:Session):
    store = db.query(Store).filter(Store.name==name).first()
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Blog with name {name} not found")
    
    return store

def create_store(request:CreateStore,db:Session):
    new_store = Store(name=request.name)
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store

def update_store(id:int,request:CreateStore,db:Session):
    
   
    store_update = db.query(Store).filter(Store.id == id).first()

    store_update.name = request.name
    db.commit()

    return store_update

def delete_store(id:int,db:Session):
    
    store_delete = db.query(Store).filter(Store.id == id).first()
    db.delete(store_delete)
    db.commit()

    if store_delete  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    return f"Store with id {id} has been successfully deleted."