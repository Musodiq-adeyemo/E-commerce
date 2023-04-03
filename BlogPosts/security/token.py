from datetime import datetime,timedelta
from jose import JWTError,jwt
from typing import Optional
from BlogPosts.schemas import Token,TokenData
from BlogPosts.security import oauth2

SECRET_KEY ='b6d504d64dd31e3d5eb1'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data:dict,expires_delta:Optional[timedelta]=None):
    to_encode = data.copy()
    if expires_delta:
        expires = datetime.utcnow() + expires_delta
    else:
        expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expires})

    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token:str,credentials_exception):
    try:
        payload=jwt.decode(token, SECRET_KEY, ALGORITHM)
        username:str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
