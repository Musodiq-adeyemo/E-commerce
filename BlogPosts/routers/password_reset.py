from fastapi import APIRouter,Depends,status,HTTPException
from BlogPosts.schemas import Token
from BlogPosts.database import get_db
from sqlalchemy.orm import Session
from BlogPosts.schemas import SchemasUser,PasswordReset,NewPassword
from BlogPosts.security.oauth2 import get_current_user
from BlogPosts.models import User
from BlogPosts.security.token import create_access_token,ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from BlogPosts.send_email import password_reset

router = APIRouter(
    tags=["Password Reset"],
    prefix="/password"
)

@router.post('/reset',summary="Reset your Forgot Password")
def reset_request(request:PasswordReset,db:Session = Depends(get_db),current_user:SchemasUser = Depends(get_current_user)):
    user = db.query(User).filter(User.email==request.email).first()

    if user is not None:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(data={"sub":user.email},expires_delta=access_token_expires)
        reset_link = f"http://localhost:8000/password/reset?token={token}"
        password_reset("Password Reset",request.email,{
        "title":f"Hey {request.username}, This is a link to reset your password",
        "Username": request.username,
        "Reset_link":reset_link
    })
        return {"access_token":token,"token_type":"Bearer"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Invalid Credentials :{request.email}")
    
@router.put('/reset',summary="Reset Password")
def reset(request:NewPassword,db:Session = Depends(get_db),current_user:SchemasUser = Depends(get_current_user)):
    return request