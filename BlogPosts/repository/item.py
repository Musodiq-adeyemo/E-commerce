from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from BlogPosts.models import Item,User
from BlogPosts.schemas import CreateItem,UpdateItem
from typing import List
from BlogPosts.security import oauth2


current_user = oauth2.get_user

def get_all_items(db:Session):
    items = db.query(Item).all()
    return items

def show_item_id(id:int,db:Session):
    item = db.query(Item).filter(Item.id==id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Item with id {id} not found")
    
    return item

def show_item_name(name:int,db:Session):
    item = db.query(Item).filter(Item.name==name).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Item with name {name} not found")
    
    return item

def create_item(request:CreateItem,db:Session):
   
    new_item = Item(
        name=request.name,
        price=request.price,
        description=request.description,
        barcode=request.barcode,
        store_id = request.store_id,
        prod_date = request.prod_date,
        user_item = request.user_item
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

def update_item(id:int,request:UpdateItem,db:Session):
    
    item_update = db.query(Item).filter(Item.id == id).first()

    item_update.name = request.name
    item_update.price = request.price
    item_update.barcode = request.barcode
    item_update.store_id = request.store_id
    
    db.commit()
    

    return item_update

def delete_item(id:int,db:Session):
    
    item_delete = db.query(Item).filter(Item.id == id).first()

    if item_delete  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")

    
    db.delete(item_delete)
    db.commit()
    
    return f"Item with id {id} has been successfully deleted."