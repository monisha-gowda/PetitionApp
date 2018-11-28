import os
import secrets
from flask import render_template, request, url_for, redirect, flash,abort
from fapp import app,bcrypt,db,login_manager
from fapp.forms import RegistrationForm,LoginForm,PetitionForm,CommentForm,AccountUpdateForm
from fapp.models import Student,Petition,Votes,Comments
from flask_login import login_user,current_user,logout_user,login_required



@app.route('/register/',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('allview'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Student(usn=form.usn.data,first_name=form.first_name.data,last_name=form.last_name.data,
        username=form.username.data,email=form.email.data,password=hashed_pwd)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created!','success')
        return redirect(url_for('login'))
    return render_template('signup.html',title='Register',form=form)


@app.route('/login/',methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('allview'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Student.query.filter_by(usn=form.usn.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user)
            flash('You have logged in','success')
            return redirect(url_for('allview'))
        else:
            flash('Unsuccessful login!! Check Username or Password','danger')
    return render_template('login.html',title='Login',form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('allview'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@app.route('/account',methods=['POST','GET'])
@login_required
def account():
    form = AccountUpdateForm()
    signed = Votes.query.filter_by(petitioner=current_user).all()
    created = Petition.query.filter_by(petitioner=current_user).all()
    my_pic = url_for('static',filename = 'profile_pics/' + current_user.profile_pic)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.profile_pic = picture_file
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash('Your Account has been Updated!!','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html',title='Account',my_pic = my_pic,form=form,signed_list = signed,created_list = created)

def save_post_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/petition_pics',picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@app.route('/Create-Petition', methods=['GET','POST'])
@login_required
def new_petition():
    form = PetitionForm()
    if form.validate_on_submit():
        if form.pet_pic.data:
            picture_file = save_post_picture(form.pet_pic.data)
            petition = Petition(title=form.title.data,department=form.department.data,content=form.content.data,image_post=picture_file,petitioner=current_user)
            db.session.add(petition)
            db.session.commit()
            flash('Your Petition has been Created!!','success')
            return redirect(url_for('allview'))
        else:
            petition = Petition(title=form.title.data,department=form.department.data,content=form.content.data,petitioner=current_user)
            db.session.add(petition)
            db.session.commit()
            flash('Your Petition has been Created!!','success')
            return redirect(url_for('allview'))
    return render_template('create.html',title='Create Petition',form=form,legend='Create Petition')

@app.route('/allview/')
def allview():
    petitions = Petition.query.all()
    return render_template('allview.html',petitions=petitions)



@app.route('/petition/<int:petition_id>',methods=['GET','POST'])
def petition(petition_id):
    comments = Comments.query.filter_by(petition_id=petition_id).all()
    vote_stat= 0
    petition = Petition.query.get_or_404(petition_id)
    upvote = Votes.query.filter_by(petition_id=petition_id).count()
    post_pic = url_for('static',filename = 'petition_pics/' + petition.image_post)
    profile_pic = url_for('static',filename = 'profile_pics/' + petition.petitioner.profile_pic)
    if current_user.is_authenticated:
        form=CommentForm()
        vote = Votes.query.filter_by(petition_id=petition_id,petitioner=current_user).first()
        if vote:
            vote_stat = 1
        if form.validate_on_submit():
            comment = Comments(petition_id=petition_id,petitioner=current_user,comment=form.comment.data)
            db.session.add(comment)
            db.session.commit()
            flash('Commented!','success')
            return redirect(url_for('petition',petition_id=petition_id))
        return render_template('petition.html',petition=petition,title=petition.title,status=vote_stat,upvote_count = upvote,form=form,comments=comments,post_pic=post_pic,profile_pic=profile_pic)
    else:
        return render_template('petition.html',petition=petition,title=petition.title,upvote_count = upvote,comments=comments,post_pic=post_pic,profile_pic=profile_pic)





@app.route('/petition/<int:petition_id>/update',methods=['GET','POST'])
@login_required
def update(petition_id):
    petition = Petition.query.get_or_404(petition_id)
    if petition.petitioner != current_user:
        abort(403)
    form = PetitionForm()
    if form.validate_on_submit():
        if form.pet_pic.data:
            picture_file = save_post_picture(form.pet_pic.data)
            petition.image_post=picture_file
        petition.title=form.title.data
        petition.department=form.department.data
        petition.content=form.content.data
        db.session.commit()
        flash('Petition Updated!!','success')
        return redirect(url_for('petition',petition_id=petition.id))
    elif request.method == 'GET':
        form.title.data = petition.title
        form.department.data = petition.department
        form.content.data=petition.content
        form.pet_pic.data=petition.image_post
    return render_template('create.html',title='Update Petition',form=form,petition=petition,legend='Update Petition')

@app.route('/petition/<int:petition_id>/delete',methods=['POST'])
@login_required
def delete_petition(petition_id):
    petition = Petition.query.get_or_404(petition_id)
    if petition.petitioner != current_user:
        abort(403)
    db.session.delete(petition)
    db.session.commit()
    flash('Petition Deleted!!','success')
    return redirect(url_for('allview'))


@app.route('/petition/<int:petition_id>/upvote',methods=['GET','POST'])
@login_required
def upvote_petition(petition_id):
    vote = Votes(petition_id=petition_id,petitioner=current_user,upvote=1)
    db.session.add(vote)
    db.session.commit()
    return redirect(url_for('petition',petition_id=petition_id))

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>Oops!! Looks like your page doesnt exist.....(╯'□')╯︵ ┻━┻ </h1>"
