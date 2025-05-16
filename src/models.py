from flask_sqlalchemy import SQLAlchemy
import enum
from typing import List
from sqlalchemy import String, Boolean, Text, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class Follower(db.Model):
    __tablename__ = 'follower'
    user_from_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'), primary_key=True)
    user_to_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'), primary_key=True)

    follower: Mapped["User"] = relationship(
        "User", foreign_keys=[user_from_id], back_populates="following")
    followed: Mapped["User"] = relationship(
        "User", foreign_keys=[user_to_id], back_populates="followers")


class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(120), nullable=False)
    username: Mapped[str] = mapped_column(
        String(60), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    posts: Mapped[List["Post"]] = relationship(
        "Post", back_populates="user", cascade="all, delete-orphan")
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="author", cascade="all, delete-orphan")
    followers: Mapped[List["Follower"]] = relationship(
        "Follower", foreign_keys="Follower.user_to_id", back_populates="followed", cascade="all, delete-orphan")
    following: Mapped[List["Follower"]] = relationship(
        "Follower", foreign_keys="Follower.user_from_id", back_populates="follower", cascade="all, delete-orphan")
    

    #uso dict en el serialze para combertir el objeto directamente a JSON

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "username": self.userName,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "followers_count": len(self.followers),
            "following_count": len(self.following)
            # do not serialize the password, its a security breach
        }


class MediaType(enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


class Media(db.Model):
    __tablename__ = 'media'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[MediaType] = mapped_column(Enum(MediaType), nullable=False)
    url: Mapped[str] = mapped_column(String(250), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), nullable=False)
    post: Mapped["Post"] = relationship("Post", back_populates="media")

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "url": self.url,
            "post_id": self.post_id

        }


class Post(db.Model):
    __tablename__ = 'post'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    caption: Mapped[str] = mapped_column(Text(), nullable=True)
    location: Mapped[str] = mapped_column(String(120), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="posts")
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan")
    media: Mapped[List["Media"]] = relationship(
        "Media", back_populates="post", cascade="all, delete-orphan")

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "caption": self.caption,
            "location": self.location,
            "comments_count": len(self.comments),
            "media_urls": [m.url for m in self.media]
        }


class Comment(db.Model):
    __tablename__ = 'comment'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    comment_text: Mapped[str] = mapped_column(Text(), nullable=False)
    author_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), nullable=False)

    author: Mapped["User"] = relationship("User", back_populates="comments")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "comment_text": self.comment_text,
            "author_id": self.author_id,
            "post_id": self.post_id,

        }


