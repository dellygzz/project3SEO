from sqlalchemy import  or_, Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
db_url = "sqlite:///database.db"
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)

base = declarative_base()

class User(base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key = True)
    username = Column(String, unique = True)
    password = Column(String)
    email = Column(String, unique = True)
    books = relationship("Book", secondary= "users_and_books", back_populates = "users")

class Book(base):
    __tablename__ = "books"

    id = Column(Integer, primary_key = True)
    google_book_id = Column(String)
    title = Column(String)
    author = Column(String)
    description = Column(String)
    users = relationship("User", secondary = "users_and_books", back_populates = "books")
    
class User_And_Book(base):
    __tablename__ = "users_and_books"

    id = Column(Integer, primary_key = True)
    book_id = Column("book_id", Integer, ForeignKey("books.id"))
    user_id = Column("user_id", Integer, ForeignKey("users.id"))
    
def init_database():
    base.metadata.create_all(engine)

def Create_User(Username, password, email):
    with Session() as session:
        #check if the user exists already
        user_exists = session.query(User).filter(or_(User.username == Username, User.email == email)).first() # could also use '|'
        if user_exists:
            return print("username or passwrod already exists")
        new_user = User(username = Username, password = password, email = email)
        session.add(new_user)
        session.commit()
        return new_user