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
    
class UserAndBook(base):
    __tablename__ = "users_and_books"

    id = Column(Integer, primary_key = True)
    book_id = Column("book_id", Integer, ForeignKey("books.id"))
    user_id = Column("user_id", Integer, ForeignKey("users.id"))
    
def init_database():
    base.metadata.create_all(engine)

# CREATE operations of DataBase
def create_user(username, password, email):
    with Session() as session:
        #check if the user exists already
        user_exists = session.query(User).filter(or_(User.username == username, User.email == email)).first() # could also use '|'
        if user_exists:
            return "username or email already exists"
        new_user = User(username = username, password = password, email = email)
        session.add(new_user)
        session.commit()
        return new_user

def create_book(google_book_id, title, author, description):
    with Session() as session:
        #dont allow duplicate books to be made, because the association table handles multiple people wanting the same book
        book_exists = session.query(Book).filter((Book.google_book_id == google_book_id)).first()

        if book_exists:
            #dont create a new book, just get the one that exists already
            return book_exists
        #else create a new book
        new_book = Book(google_book_id = google_book_id, title = title, author = author, description = description)
        session.add(new_book)
        session.commit()
        return new_book

def create_user_and_book(user_id, google_book_id, title, author, description):
    with Session() as session:
        user_exists = session.query(User).filter(User.id == user_id).first()
        #check if the user already exists, cuz no point in adding book to a non-existent user
        if not user_exists:
            print("username does not exist")
            return False

        book = session.query(Book).filter(Book.google_book_id == google_book_id).first()

        if not book:
            book = Book(google_book_id = google_book_id, title = title, author = author, description = description)
            session.add(book)

        if book in user_exists.books:
            print("User already put this book in their reading log")
            return False
        #cool way to simplify access through proxy, since we made a relationship between the two tables we can use this.
        user_exists.books.append(book)
        session.commit()
        return True

#READ operations of database
def get_user_books(user_id):
    with Session() as session:
        user_exists = session.query(User).filter(User.id == user_id).first()
        if not user_exists:
            return "Invalid User ID or User does not exist"
        if not user_exists.books:
            #return an empty list, since 
            return []
        #use list comprehension to return the details we want
        return [{"id" : book.google_book_id, "title" : book.title, "author" : book.author, "description" : book.description} for book in user_exists.books]

def get_user_by_id(user_id):
    #get the user by their ID
    with Session() as session:
        #check if the user exists already
        return session.query(User).filter(User.id == user_id).first()

def get_user_by_identifier(identifier):
    with Session() as db_session:
        #check if the user exists already
        return db_session.query(User).filter(or_(User.username == identifier, User.email == identifier)).first()
    
#DELETE operations of database
def remove_books_from_user(user_id, google_book_id):
    with Session() as session:
        user_exists = session.query(User).filter(User.id == user_id).first()
        if not user_exists:
            return "Invalid User ID or User does not exist"
        
        book = session.query(Book).filter(Book.google_book_id == google_book_id).first()
        if not book:
            return "Book not found"
        if book in user_exists.books:
            user_exists.books.remove(book)
            session.commit()
            return True
        else:
            return "Book not in user's reading list"