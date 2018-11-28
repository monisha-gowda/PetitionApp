from sqlalchemy import text
from datetime import datetime
from fapp import db,login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(student_id):
    return Student.query.get(int(student_id))



class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    usn = db.Column(db.String(10),unique=True,nullable=False)
    first_name = db.Column(db.String(20),nullable=False)
    last_name=db.Column(db.String(20))
    username = db.Column(db.String(20),unique=True, nullable=False)
    email = db.Column(db.String(120),unique=True, nullable=False)
    password = db.Column(db.String(60),nullable=False)
    profile_pic = db.Column(db.String(20),default='default.jpg')
    petitions = db.relationship('Petition',backref='petitioner',lazy=True)
    votes = db.relationship('Votes',backref='petitioner',lazy=True)
    comments = db.relationship('Comments',backref='petitioner',lazy=True)
    def __repr__(self):
        return f"Student('{self.username}')"

class Petition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    department = db.Column(db.String(100),nullable=False)
    content = db.Column(db.Text,nullable=False)
    image_post = db.Column(db.String(1000),default='default.jpg')
    student_id = db.Column(db.Integer,db.ForeignKey('student.id'), nullable=False)
    votes = db.relationship('Votes',backref='petition',lazy=True)
    comments = db.relationship('Comments',backref='petition',lazy=True)

    def __repr__(self):
        return f"Petition('{self.title}',''{self.date_posted}'','{self.content}','{self.image_post}',)"



class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    petition_id = db.Column(db.Integer,db.ForeignKey('petition.id'),nullable=False)
    student_id = db.Column(db.Integer,db.ForeignKey('student.id'),nullable=False)
    upvote = db.Column(db.Integer,nullable=False)

    def __repr__(self):
       return f"Votes('{self.petition_id}','{self.student_id}',{self.upvote}')"



class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    petition_id = db.Column(db.Integer,db.ForeignKey('petition.id'),nullable=False)
    student_id = db.Column(db.Integer,db.ForeignKey('student.id'),nullable=False)
    comment = db.Column(db.Text,nullable=False)

    def __repr__(self):
       return f"Comments('{self.petition_id}','{self.student_id}','{self.comment}')"
