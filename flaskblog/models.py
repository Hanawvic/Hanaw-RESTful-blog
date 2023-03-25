from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import relationship

from flaskblog import db

current_year = datetime.now().year


# User table
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    confirmed = db.Column(db.Boolean, default=False)
    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    # *******Add parent relationship*******#
    # "comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comment", back_populates="comment_author")

    def __init__(self, email, password, name, confirmed):
        self.email = email
        self.password = password
        self.name = name
        self.confirmed = confirmed

    def num_posts(self):
        return len(self.posts)

    # every User object called is displayed by its name (no need to add name attribute : user instead of user.name)
    def __repr__(self):
        return f'{self.name}'


# CONFIGURE TABLE for blog posts
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.String(1000), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    # ***************Parent Relationship*************#
    comments = relationship("Comment", back_populates="parent_post")

    def __init__(self, title, subtitle, post_date, body, img_url, author):
        self.title = title
        self.subtitle = subtitle
        self.date = post_date
        self.body = body
        self.img_url = img_url
        self.author = author

    # Optional: this will allow each post object to be identified by its title when printed.
    def __repr__(self):
        return f'Post {self.title}'


# Configure comment table
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    # *******Add child relationship*******#
    # "users.id" The users refers to the tablename of the Users class.
    # "comments" refers to the comments property in the User class.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    # *******Add child relationship*******#
    # "blog_posts.id" The users refers to the tablename of the BlogPost class.
    # "comments" refers to the comments property in the BlogPost class.
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, text, comment_author, parent_post):
        self.text = text
        self.comment_author = comment_author
        self.parent_post = parent_post

    def __repr__(self):
        return f"<Comment {self.id}>"


# Define a model for notifications in the database
class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
