from sqlalchemy import Integer,Column,String,DateTime,ForeignKey,Float,LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy import func
from BlogPosts.database import Base,engine




class User(Base):
    __tablename__= "user"
    id = Column(Integer(), primary_key=True)
    email = Column(String(200), unique=True)
    username = Column(String(100),unique=True)
    password =Column(String(20))
    firstname = Column(String(100),nullable=False)
    lastname = Column(String(100),nullable=False)
    created_at =Column(DateTime(timezone=True), server_default = func.now())
    blogs= relationship('BlogPost',back_populates ="creator")
    item_user =relationship('Item',back_populates = "user")

    def __repr__(self):
        return f"User {self.username}"

class UserImage(Base):
    __tablename__= "userimages"
    id = Column(Integer(), primary_key=True)
    name = Column(String(200))
    img = Column(LargeBinary())
    minetype = Column(String(100))
    user_id =Column(Integer())

    def __repr__(self):
        return f"UserImage {self.name}"

class BlogPost(Base):
    __tablename__= "blogposts"
    id = Column(Integer(), primary_key=True)
    title = Column(String(100),nullable=False)
    content = Column(String(1000),nullable=False)
    author = Column(String(20),nullable=False)
    posted_at = Column(DateTime(timezone=True), server_default = func.now())
    poster_id = Column(Integer())
    user_id = Column(Integer(), ForeignKey('user.id'))
    creator = relationship('User',back_populates="blogs")

    def __repr__(self):
        return f"BlogPost {self.title}"

class PostImage(Base):
    __tablename__= "postimages"
    id = Column(Integer(), primary_key=True)
    name = Column(String(200))
    img = Column(LargeBinary())
    minetype = Column(String(100))
    post_id =Column(Integer())

    def __repr__(self):
        return f"PostImage {self.name}"

class Item(Base):
    __tablename__= "items"
    id = Column(Integer(), primary_key=True)
    name = Column(String(100),nullable=False)
    barcode = Column(String(100),nullable=False)
    description = Column(String(1000),nullable=False)
    price = Column(Float(precision=2),nullable=False)
    prod_date = Column(DateTime(timezone=True))
    store_id = Column(Integer(),ForeignKey("stores.id"),nullable=False)
    user_item = Column(Integer(),ForeignKey('user.id'))
    store = relationship('Store',back_populates="items")
    user = relationship('User',back_populates="item_user")

    def __repr__(self):
        return f"Item {self.name}"


class ItemImage(Base):
    __tablename__= "itemimages"
    id = Column(Integer(), primary_key=True)
    name = Column(String(200))
    img = Column(LargeBinary())
    minetype = Column(String(100))
    item_id =Column(Integer())

    def __repr__(self):
        return f"ItemImage {self.name}"

class Store(Base):
    __tablename__= "stores"
    id = Column(Integer(), primary_key=True)
    name = Column(String(100),nullable=False)
    items = relationship('Item',back_populates="store")

    def __repr__(self):
        return f"Store {self.name}"

Base.metadata.create_all(bind=engine)