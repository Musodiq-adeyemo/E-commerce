from fastapi import APIRouter,Depends,status,UploadFile,File,HTTPException
from BlogPosts.schemas import ShowItem,SchemasUser,CreateItem,UpdateItem,ItemImg
from typing import List
from sqlalchemy.orm import Session
from BlogPosts.database import get_db
from BlogPosts.security.oauth2 import get_current_user
from BlogPosts.repository import item
from werkzeug.utils import secure_filename
from BlogPosts.models import Item,ItemImage
import shutil
from BlogPosts.security import oauth2
import io
import base64


router = APIRouter(
    tags=["ITEMS"],
    prefix = "/items"
)


@router.get('/all',response_model= List[ShowItem],summary="Get all the Items in Store")
def get_all_items(db:Session = Depends(get_db),current_user:SchemasUser = Depends(get_current_user)):
    return item.get_all_items(db)

@router.get('/{id}',response_model= ShowItem,summary="Get Item in Store by Id")
def show_item_id(id:int,db:Session = Depends(get_db),current_user:SchemasUser = Depends(get_current_user)):
    return item.show_item_id(id,db)

@router.get('/{name}',response_model= ShowItem,summary="Get Item in Store by Name")
def show_item_name(name:str,db:Session = Depends(get_db),current_user:SchemasUser = Depends(get_current_user)):
    return item.show_item_name(name,db)

@router.post('/create', response_model=ShowItem,status_code = status.HTTP_201_CREATED,summary="Create an Item")
def create_item(request:CreateItem,db:Session = Depends(get_db),current_user:SchemasUser = Depends(get_current_user)):
    return item.create_item(request,db)

@router.put('/update/{id}',response_model=ShowItem, status_code = status.HTTP_202_ACCEPTED,summary="Update an Item in Store")
def update_item(id,request:UpdateItem,db:Session = Depends(get_db),current_user:SchemasUser = Depends(get_current_user)):
    return item.update_item(id,request,db)

@router.delete('/delete/{id}', status_code = status.HTTP_204_NO_CONTENT,summary="Delete a an Item in Store")
def delete_item(id,db:Session = Depends(get_db),current_user:SchemasUser = Depends(get_current_user)):
    return item.delete_item(id,db)

@router.post("/upload",summary="Upload your Item picture")
def upload(item_id:int,db:Session = Depends(get_db),file:UploadFile = File(...),current_user:SchemasUser = Depends(oauth2.get_current_user)):
    with open(f"BlogPosts/static/itemimages/{file.filename}","wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    name = secure_filename(file.filename)
    mimetype = file.content_type
    item_upload = ItemImage(img= file.file.read(),minetype=mimetype,name=name,item_id=item_id)
    db.add(item_upload)
    db.commit()
    return f"{name} has been Successfully Uploaded"

@router.get("/upload/{id}",response_model=ItemImg,summary="Get item image by id")
def items_image(id:int,db:Session = Depends(get_db),current_user:SchemasUser = Depends(oauth2.get_current_user)):
    images = db.query(ItemImage).filter(ItemImage.id == id).first()
    if not images:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No image uploaded yet")
    
    return images

