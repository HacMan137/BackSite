import os
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from backsite.db.schema import Base
from backsite.db.connection import create_connection
from uuid import uuid4
from datetime import datetime
from elasticsearch import Elasticsearch

ELASTIC_HOST = os.getenv("ELASTIC_HOST", "elastic")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "backsite")

def get_elastic_connection():
    return Elasticsearch(f"https://{ELASTIC_HOST}:9200", http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)

class Post(Base):
    __tablename__ = "post"

    post_id = Column(Integer, primary_key = True, autoincrement = True)
    title = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    user_id = Column(ForeignKey("backsite_user.user_id", ondelete="CASCADE"), nullable=False)
    replying_to = Column(ForeignKey("post.post_id"), nullable=True)

    author = relationship("User", back_populates="posts")
    original = relationship("Post", back_populates="replies", remote_side=[post_id])
    replies = relationship("Post", back_populates="original")

    @property
    def json(self):
        return {
            "post_id": self.post_id,
            "title": self.title,
            "author": self.author.json,
            "timestamp": self.timestamp.isoformat(),
            "replying_to": self.replying_to,
        }

    @property
    def content(self):
        es = get_elastic_connection()
        doc = es.get(index="posts", id=self.post_id)["_source"]
        return doc['content']
    
    @content.setter
    def content(self, value):
        es = get_elastic_connection()
        doc = self.json
        doc['content'] = value
        es.update(index="posts", id=self.post_id, body={"doc": doc})

    @classmethod
    def createPost(cls, content, author_id, title=None, replying_to_id = None):
        # Add post to SQL DB
        conn = create_connection()
        postObj = cls(
            user_id=author_id,
            title=title,
            replying_to=replying_to_id
        )
        conn.add(postObj)
        conn.commit()
        # Add post to ElasticSearch
        doc = postObj.json
        doc['content'] = content
        es = get_elastic_connection()
        es.index(index="posts", id=postObj.post_id, document=doc)
        # Return SQL Object
        return postObj