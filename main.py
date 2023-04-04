from fastapi import FastAPI,Request,Depends,Form,status,UploadFile,File,HTTPException
from BlogPosts.routers import blog
from BlogPosts.routers import user
from BlogPosts.routers import authentication
from BlogPosts.routers import password_reset
from BlogPosts.routers import store
from BlogPosts.routers import item
from fastapi.responses import HTMLResponse,RedirectResponse,Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from BlogPosts.models import BlogPost,User,Item,Store,ItemImage,UserImage,PostImage
from sqlalchemy.orm import Session
from BlogPosts.database import get_db
from BlogPosts.schemas import Setting
from fastapi_jwt_auth import AuthJWT
from BlogPosts.security.hashing import Hash
from datetime import timedelta
from datetime import datetime
import shutil
from werkzeug.utils import secure_filename

access_token_expire =timedelta(days=30)
refresh_token_expire = timedelta(days=1)
new_access_token_expire = timedelta(days=7)
access_algorithm = "HS384"
refresh_algorithm = "HS512"

@AuthJWT.load_config
def get_config():
    return Setting()

app= FastAPI(
    docs_url = "/docs",
    redoc_url= "/redocs",
    title="SIRMUSO BLOGSITE API",
    description="FRAMEWORK FOR SIRMUSO BLOGSITE API",
    version="4.0",
    openapi_url="/api/v2/openapi.json"
    
)

app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(blog.router)
app.include_router(store.router)
app.include_router(item.router)
app.include_router(password_reset.router)

templates = Jinja2Templates(directory="BlogPosts/templates")
app.mount("/static",StaticFiles(directory="BlogPosts/static"),name="static")

def get_user(id:int,session=get_db):
    db = next(session())
    user = db.query(User).filter(User.id==id).first()
    return user

# Homepge
@app.get('/',response_class=HTMLResponse,tags=["Template"])
def home(request: Request, db:Session = Depends(get_db)):
    blogs = db.query(BlogPost).all()
    users = db.query(User).all()
    images = db.query(UserImage).all()
    pimages = db.query(PostImage).all()
    for user in users:
        no_of_blog = len(user.blogs)
    return templates.TemplateResponse("home.html",{"request":request,"blogs":blogs,"pimages":pimages,"images":images,"users":users,"no_of_blog":no_of_blog})
# User Profile
@app.get('/users',response_class=HTMLResponse,tags=["Template"])
def get_users(request: Request, db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

        current_user = Authorize.get_jwt_subject()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    users = db.query(User).all()
    images = db.query(UserImage).all()
    return templates.TemplateResponse("users.html",{"request":request,"users":users,"images":images,"current_user":current_user})

# All items available
@app.get('/items',response_class=HTMLResponse,tags=["Template"])
def get_items(request: Request, db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    items = db.query(Item).all()
    images = db.query(ItemImage).all()
    return templates.TemplateResponse("items.html",{"request":request,"items":items,"images":images})

# Check Store for all items
@app.get('/store',response_class=HTMLResponse,tags=["Template"])
def get_stores(request: Request, db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    stores = db.query(Store).all()
    return templates.TemplateResponse("store.html",{"request":request,"stores":stores})

# Item by  ID
@app.get('/content/{id}',response_class=HTMLResponse,tags=["Template"])
def get_items(id:int,request: Request, db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    item = db.query(Item).filter(Item.id == id).first()
    images = db.query(ItemImage).all()
    return templates.TemplateResponse("content.html",{"request":request,"item":item,"images":images})

# USER REGISTRATION
@app.get("/register",response_class=HTMLResponse,tags=["Template"])
def signup(request: Request):
    return templates.TemplateResponse("signup.html",{"request":request})

@app.post("/register",response_class=HTMLResponse,tags=["Template"])
def signup(request: Request,username:str=Form(...),email:str=Form(...),password:str=Form(...),password2:str=Form(...),firstname:str=Form(...),lastname:str=Form(...), db:Session = Depends(get_db)):
    user_exist = db.query(User).filter(User.username==username).first()
    email_exist = db.query(User).filter(User.email==email).first()
    errors=[]

    if email_exist:
        errors.append("Email Already Exist,Login or Change Email.")

    if user_exist:
        errors.append("Username Already Exist,Try another one.")
    
    if not email :
        errors.append("Not a proper Email")

    if password == password2 and len(password) > 7 :
        new_user = User(username=username,lastname=lastname,firstname=firstname,email=email,password=Hash.bcrypt(password))
        db.add(new_user)
        db.commit()
        redirect_url = "/signin"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    
    if len(errors) > 0 :
        return templates.TemplateResponse("signup.html",{"request":request,"errors":errors})
    else:
        errors.append("Password dont match or less than 8 charaters")
        return templates.TemplateResponse("signup.html",{"request":request,"errors":errors})

# UPDATE ACCOUNT
@app.get('/update_user/{id}',response_class=HTMLResponse,tags=["Template"])
def update_user(request: Request,id:int,db:Session=Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    user = db.query(User).filter(User.id == id).first()
    return templates.TemplateResponse("users_update.html",{"request":request,"user":user})

@app.post('/update_user/{id}',response_class=HTMLResponse,tags=["Template"])
def update_user(request: Request,id:int, db:Session = Depends(get_db),username:str=Form(...),firstname:str=Form(...),lastname:str=Form(...)):
    
    user_update = db.query(User).filter(User.id == id).first()

    user_update.username = username
    user_update.lastname = lastname
    user_update.firstname = firstname
    db.commit()

    redirect_url = "/users"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)

#DELETE ACCOUNT
@app.get('/delete_user/{id}',tags=["Template"])
def delete_user(request: Request,id:int, db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    user_delete = db.query(User).filter(User.id == id).first()

    db.delete(user_delete)
    db.commit()
    redirect_url = "/signup"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    
# UPLOAD PROFILE PICTURE
@app.get("/upload_pimage",response_class=HTMLResponse,tags=["Template"])
def upload_pimage(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("upload_profile.html",{"request":request})

@app.post("/upload_pimage",response_class=HTMLResponse,tags=["Template"])
def upload_pimage(request: Request,user_id:str=Form(...),file:UploadFile = File(...),db:Session = Depends(get_db)):
    try:
        with open(f"BlogPosts/static/userimages/{file.filename}","wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        name = secure_filename(file.filename)
        mimetype = file.content_type

        image_upload = UserImage(img = file.file.read(),minetype=mimetype, name=name,user_id=user_id)
        db.add(image_upload)
        db.commit()
        redirect_url = "/users"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except:
        return templates.TemplateResponse("upload_profile.html",{"request":request,"image_upload":image_upload})


#LOGIN AUTHENTICATION
@app.get("/signin",tags=["Template"])
def login(request: Request):
    return templates.TemplateResponse("signin.html",{"request":request})


@app.post("/signin",tags=["Template"])
def login(request: Request,response:Response,Authorize:AuthJWT=Depends(),username:str=Form(...),password:str=Form(...),db:Session = Depends(get_db)):
    errors = []
    user = db.query(User).filter(User.username==username).first()

    if user is None:
        errors.append("Invalid Credentials,Please check username or password")
        return templates.TemplateResponse("signin.html",{"request":request,"errors":errors})
    
    verify_password = Hash.verify_password(password,user.password)

    if (username == user.username and verify_password):
        access_token = Authorize.create_access_token(subject=user.username,expires_time=access_token_expire)
        redirect_url = "/users"
        resp = RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
        Authorize.set_access_cookies(access_token,resp)
        return resp
    else:
        errors.append("Invalid Credentials,Please check username or password")
        return templates.TemplateResponse("signin.html",{"request":request,"errors":errors})

@app.get("/logout")
def logout(Authorize:AuthJWT=Depends()):
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies
    
    redirect_url = "/"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)


# CREATE BLOG POST
@app.get('/create_post',response_class=HTMLResponse,tags=["Template"])
def create_post(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("new_post.html",{"request":request})

@app.post('/create_post',response_class=HTMLResponse,tags=["Template"])
def create_post(request: Request, db:Session = Depends(get_db),title:str=Form(...),content:str=Form(...),author:str=Form(...),user_id:int=Form(...)):
    errors = []
    try:
        new_blog = BlogPost(title=title,content=content,author=author,user_id = user_id)
        db.add(new_blog)
        db.commit()
        db.refresh(new_blog)
        redirect_url = "/"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except :
        errors.append("Something went Wrong make sure you are doing the right thing")
        return templates.TemplateResponse("new_post.html",{"request":request,"errors":errors})

# EDIT BLOG POST
@app.get('/edit_post/{id}',response_class=HTMLResponse,tags=["Template"])
def update_post(request: Request,id:int,db:Session=Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    blog = db.query(BlogPost).filter(BlogPost.id == id).first()
    return templates.TemplateResponse("edit.html",{"request":request,"blog":blog})

@app.post('/edit_post/{id}',response_class=HTMLResponse,tags=["Template"])
def update_post(request: Request,id:int, db:Session = Depends(get_db),title:str=Form(...),content:str=Form(...)):
    errors = []
    try:
        update_post = db.query(BlogPost).filter(BlogPost.id == id).first()
        update_post.title=title
        update_post.content=content
        db.commit()
        redirect_url = "/"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except :
        errors.append("Something went Wrong, You are not authorized to edit this post.")
        return templates.TemplateResponse("edit.html",{"request":request,"errors":errors})

#DELETE BLOG POST
@app.get('/delete_post/{id}',tags=["Template"])
def delete_post(request: Request,id:int, db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    delete_post = db.query(BlogPost).filter(BlogPost.id == id).first()
    db.delete(delete_post)
    db.commit()
    redirect_url = "/"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    
#POST IMAGE UPLOAD
@app.get("/upload_postimage",response_class=HTMLResponse,tags=["Template"])
def upload_postimage(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("upload_postimage.html",{"request":request})

@app.post("/upload_postimage",response_class=HTMLResponse,tags=["Template"])
def upload_postimage(request: Request,post_id:int=Form(...),file:UploadFile = File(...),db:Session = Depends(get_db)):
    try:

        with open(f"BlogPosts/static/postimages/{file.filename}","wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        name = secure_filename(file.filename)
        mimetype = file.content_type

        image_post = PostImage(img = file.file.read(),minetype=mimetype, name=name,post_id=post_id)
        db.add(image_post)
        db.commit()
        redirect_url = "/"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except:
        return templates.TemplateResponse("upload_postimage.html",{"request":request})

# CREATE ITEM
@app.get('/create_item',response_class=HTMLResponse,tags=["Template"])
def create_item(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("create_item.html",{"request":request})

@app.post('/create_item',response_class=HTMLResponse,tags=["Template"])
def create_item(request: Request, db:Session = Depends(get_db),name:str=Form(...),description:str=Form(...),barcode:str=Form(...),store_id:int=Form(...),user_item:int=Form(...),prod_date:datetime=Form(...),price:float=Form(...)):
    errors = []
    try:
        new_item = Item(
        name=name,
        price=price,
        description=description,
        barcode=barcode,
        store_id = store_id,
        prod_date = prod_date,
        user_item = user_item
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        redirect_url = "/items"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except :
        errors.append("Something went Wrong make sure you are doing the right thing")
        return templates.TemplateResponse("create_item.html",{"request":request,"errors":errors})

# EDIT ITEM
@app.get('/edit_item/{id}',response_class=HTMLResponse,tags=["Template"])
def update_item(request: Request,id:int,db:Session=Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    item = db.query(Item).filter(Item.id == id).first()
    return templates.TemplateResponse("edit_item.html",{"request":request,"item":item})

@app.post('/edit_item/{id}',response_class=HTMLResponse,tags=["Template"])
def update_item(request: Request,id:int, db:Session = Depends(get_db),name:str=Form(...),barcode:str=Form(...),store_id:int=Form(...),price:float=Form(...),description:str=Form(...)):
    errors = []
    try:
        item_update = db.query(Item).filter(Item.id == id).first()

        item_update.name = name
        item_update.price = price
        item_update.barcode = barcode
        item_update.store_id = store_id
        item_update.description = description
        
        db.commit()
        redirect_url = "/items"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except :
        errors.append("Something went Wrong, You are not authorized to edit this post.")
        return templates.TemplateResponse("edit_item.html",{"request":request,"errors":errors})

#DELETE ITEM
@app.get('/delete_item/{id}',tags=["Template"])
def delete_item(request: Request,id:int, db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    item_delete = db.query(Item).filter(Item.id == id).first()
    db.delete(item_delete)
    db.commit()
    redirect_url = "/items"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    
#Upload Item Image
@app.get("/upload_item",response_class=HTMLResponse,tags=["Template"])
def upload_item(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("upload_item.html",{"request":request})

@app.post("/upload_item",response_class=HTMLResponse,tags=["Template"])
def upload_item(request: Request,item_id:str=Form(...),file:UploadFile = File(...),db:Session = Depends(get_db)):
    try:
        with open(f"BlogPosts/static/itemimages/{file.filename}","wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

            name = secure_filename(file.filename)
            mimetype = file.content_type
            item_upload = ItemImage(img= file.file.read(),minetype=mimetype,name=name,item_id=item_id)
            db.add(item_upload)
            db.commit()
            redirect_url = "/items"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except:
        return templates.TemplateResponse("upload_profile.html",{"request":request,"item_upload":item_upload})

# CREATE STORE
@app.get('/create_store',response_class=HTMLResponse,tags=["Template"])
def create_store(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("new_post.html",{"request":request})

@app.post('/create_store',response_class=HTMLResponse,tags=["Template"])
def create_store(request: Request, db:Session = Depends(get_db),name:str=Form(...)):
    errors = []
    try:
        new_store = Store(name=name)
        db.add(new_store)
        db.commit()
        db.refresh(new_store)
        redirect_url = "/store"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except :
        errors.append("Something went Wrong make sure you are doing the right thing")
        return templates.TemplateResponse("new_post.html",{"request":request,"errors":errors})

# EDIT ITEM
@app.get('/edit_store/{id}',response_class=HTMLResponse,tags=["Template"])
def update_store(request: Request,id:int,db:Session=Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    store = db.query(Store).filter(Store.id == id).first()
    return templates.TemplateResponse("edit_store.html",{"request":request,"store":store})

@app.post('/edit_store/{id}',response_class=HTMLResponse,tags=["Template"])
def update_store(request: Request,id:int, db:Session = Depends(get_db),name:str=Form(...)):
    errors = []
    try:
        store_update = db.query(Store).filter(Store.id == id).first()

        store_update.name = name
        db.commit()

        redirect_url = "/store"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except :
        errors.append("Something went Wrong, You are not authorized to edit this post.")
        return templates.TemplateResponse("edit_store.html",{"request":request,"errors":errors})

#DELETE STORE
@app.get('/delete_store/{id}',tags=["Template"])
def delete_store(request: Request,id:int, db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    store_delete = db.query(Store).filter(Store.id == id).first()
    db.delete(store_delete)
    db.commit()
    redirect_url = "/store"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    
#ABOUT PAGE
@app.get("/about",response_class=HTMLResponse,tags=["Template"])
def about(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("about.html",{"request":request})
