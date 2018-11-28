from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from flask_login import current_user
from wtforms import StringField,PasswordField,SubmitField,TextAreaField
from fapp.models import Student,Petition
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError

class RegistrationForm(FlaskForm):
    usn = StringField('USN', validators=[DataRequired(),Length(max=10)])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_usn(self,usn):
        user = Student.query.filter_by(usn=usn.data).first()
        if user:
            raise ValidationError('The USN is already registered')

    def validate_username(self,username):
        user = Student.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('The Username already exists')

    def validate_email(self,email):
        user = Student.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('The Email is already registered')

class LoginForm(FlaskForm):
    usn = StringField('USN',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField('Login')


class PetitionForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    department = StringField('Concerned Department',validators=[DataRequired()])
    pet_pic = FileField('Put a Relevant Picture',validators=[FileAllowed(['jpg','png'])])
    content = TextAreaField('Content',validators=[DataRequired()])
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    comment = TextAreaField('Comment',validators=[DataRequired()])
    submit = SubmitField('Submit')

class AccountUpdateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired(),Email()])
    picture = FileField('Profile Picture',validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')


    def validate_username(self,username):
        if username.data != current_user.username:
            user = Student.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('The Username already exists')

    def validate_email(self,email):
        if email.data != current_user.email:
            user = Student.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('The Email is already registered')
