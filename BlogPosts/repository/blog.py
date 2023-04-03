from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from BlogPosts.models import BlogPost,User
from BlogPosts.schemas import UpdateBlog,SchemasBlog
from typing import List
from BlogPosts.security import oauth2



def get_all(db:Session):
    blogs = db.query(BlogPost).all()
    return blogs

def create_post(request:SchemasBlog,db:Session):
    new_blog = BlogPost(title=request.title,content=request.content,author=request.author,user_id = request.user_id)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

def delete_post(id:int,db:Session):
    
    post_delete = db.query(BlogPost).filter(BlogPost.id == id).first()

    if post_delete  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")

    db.delete(post_delete)
    db.commit()

    return f"Blog Post with id {id} has been successfully deleted."
    """
    blog = db.query(BlogPost).filter(BlogPost.id==id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Blog with id {id} not found")
    blog.delete(synchronize_session=False)
    db.commit()
    return f"Blog Post with id {id} has been successfully deleted."
    """
    
def update_post(id:int,request:UpdateBlog,db:Session):
    #blog = db.query(BlogPost).filter(BlogPost.id==id)
   
    post_update = db.query(BlogPost).filter(BlogPost.id == id).first()

    post_update.title = request.title
    post_update.content = request.content

    db.commit()

    return post_update
    """
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Blog with id {id} not found")
    blog.update(request)
    db.commit()
    return f"Blog Post with id {id} has been successfully Updated."
     """
def show_post(id:int,db:Session):
    blog = db.query(BlogPost).filter(BlogPost.id==id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Blog with id {id} not found")
    
    return blog

def get_title(blog_title:str,db:Session):
    title_blog = db.query(BlogPost).filter(BlogPost.title == blog_title).first()
    if not title_blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Blog post with title {blog_title} is not available")
    
    return title_blog

def get_title_author(title:str,author:str,db:Session):
    blog_title_author = db.query(BlogPost).filter(BlogPost.title==title,BlogPost.author==author).first()
    if not blog_title_author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Blog post with title {title} and written by {author} is not available")
    
    return blog_title_author