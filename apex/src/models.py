from src.ext.database import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(512))
    api_key = db.Column(db.String(512), default=None)
    email = db.Column(db.String(512), default=None)
    stmp_password = db.Column(db.String(512), default=None)
    admin = db.Column(db.Boolean, default=False)
    rearchresults = db.relationship('SearchResult', backref='user')
    created_at = db.Column(db.DateTime, default=db.func.now())


    def __repr__(self):
        return '<User %r>' % self.username
    
    
class SearchResult(db.Model):
    __tablename__ = 'searchresults'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512))
    result_id = db.Column(db.String(512))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=db.func.now())
