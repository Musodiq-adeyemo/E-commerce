from fastapi import APIRouter,Depends,status,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from BlogPosts.database import get_db
from BlogPosts.models import User
from BlogPosts.security.hashing import Hash
from BlogPosts.security.token import create_access_token,ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from BlogPosts.schemas import UserLogin,Token
from typing import List

router = APIRouter(
    tags=["Authentication"]
)


@router.post('/login',response_model=Token,summary="Login Your Account")
def login(request:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user = db.query(User).filter(User.username==request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Invalid Credentials,Please check username: {request.username}")
    verified_password = Hash.verify_password(request.password,user.password)
    if user and verified_password:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub":user.username},expires_delta=access_token_expires)
        return {"access_token":access_token,"token_type":"Bearer"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Invalid CredentialsPlease check Password: {request.password}")