from flask import render_template, flash, request, redirect, url_for
from flaskapp import app, db, bcrypt
from flaskapp.forms import LoginForm, RegistrationForm, UpdateAccountForm, searchForm, reserveForm, UploadcsvForm
from flaskapp.models import User, ReservedUsername, Notifications
from flask_login import login_user, current_user, logout_user, login_required
import os
import secrets
from PIL import Image
from io import TextIOWrapper
import csv

@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and user.status == 'blocked':
            flash('Your account is blocked!!', 'danger')
            return render_template('login.html',title = 'Login', form = form)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful.','danger')
    return render_template('login.html',title = 'Login', form = form)

@app.route("/regUser", methods = ['POST', 'GET'])
def regUser():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, category='user', status='active')
        db.session.add(user)
        db.session.commit()
        flash ('Your account has been created! you are now able to login','success')
        return redirect(url_for('login'))
    return render_template('reg.html', form = form, title = 'Register')

@app.route("/home", methods=['GET', 'POST'])
def home():
    user = User.query.all()
    return render_template("home.html", title = 'Home')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/usersview", methods=['GET', 'POST'])
@login_required
def usersview():
    if current_user.category != 'admin':
        return redirect(url_for('home'))
    form = searchForm()
    Users = User.query.order_by(User.username).all()
    if form.validate_on_submit():
        page = request.args.get('page', 1, type=int)
        users = User.query.filter_by(status = 'active').filter(User.username.like('%' + form.username.data + '%')).paginate(page = page, per_page = 5)
        return render_template("viewUsers.html", users = users, title = 'Search Result')
    page = request.args.get('page', 1, type=int)
    users = User.query.filter_by(category = 'user').filter_by(status = 'active').order_by(User.id.asc()).paginate(page = page, per_page = 5)
    return render_template("viewUsers.html", users = users, title = 'Users',  form=form)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)

    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn


@app.route("/account", methods = ['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename = 'images/' + current_user.image_file)
    return render_template('account.html',title = 'Account', image_file = image_file, form=form)

@app.route("/singleUserView/<int:id>")
@login_required
def singleUserView(id):
    if current_user.category != 'admin':
        return redirect(url_for('home'))
    user = User.query.get_or_404(id)
    image_file = url_for('static', filename = 'images/' + user.image_file)
    return render_template('singleUserView.html', user = user, image_file = image_file, title = user.username)



@app.route("/changeUsername/<int:id>", methods=['GET', 'POST'])
@login_required
def changeUsername(id):
    if current_user.category != 'admin':
        return redirect(url_for('home'))
    user = User.query.get_or_404(id)
    user.username = request.form['newUsername']
    db.session.commit()
    return redirect(url_for('singleUserView', id=id))



@app.route("/addAdmin", methods = ['POST', 'GET'])
def addAdmin():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, category='subadmin', status='active')
        db.session.add(user)
        db.session.commit()
        flash ('The account has been created!','success')
        return redirect(url_for('login'))
    return render_template('addAdmin.html', form = form, title = 'Add Sub-Admin')


@app.route("/subAdminView")
@login_required
def subAdminView():
    if current_user.category != 'admin':
        return redirect(url_for('home'))
    page = request.args.get('page', 1, type=int)
    users = User.query.filter_by(category = 'subadmin').filter_by(status = 'active').order_by(User.id.asc()).paginate(page = page, per_page = 5)
    return render_template("viewUsers.html", users = users, title = 'SubAdmins')


@app.route("/editSubAdmin/<int:id>", methods=['GET', 'POST'])
@login_required
def editSubAdmin(id):
    if current_user.category != 'admin':
        return redirect(url_for('home'))
    user = User.query.get_or_404(id)
    user.username = request.form['newUsername']
    user.email = request.form['newEmail']
    db.session.commit()
    return redirect(url_for('singleUserView', id=id))

@app.route("/deleteUser/<int:id>", methods=['GET', 'POST'])
@login_required
def deleteUser(id):
    if current_user.category != 'admin':
        return redirect(url_for('home'))
    user = User.query.filter_by(id=id).first()
    userCat = user.category
    User.query.filter_by(id=id).delete()
    db.session.commit()
    flash('User Account Deleted','info')
    if userCat == 'subadmin':
        return redirect(url_for('subAdminView'))
    else:
        return redirect(url_for('usersview'))

@app.route("/blockUser/<int:id>", methods=['GET','POST'])
@login_required
def blockUser(id):
    if current_user.category != 'admin':
        return redirect(url_for('home'))
    user = User.query.filter_by(id=id).first()
    userCat = user.category
    user.status = 'blocked'
    db.session.commit()
    flash('User Account Blocked','info')
    if userCat == 'subadmin':
        return redirect(url_for('subAdminView'))
    else:
        return redirect(url_for('usersview'))

@app.route("/blockedSubAdminView")
@login_required
def blockedSubAdminView():
    if current_user.category != 'admin':
        return redirect(url_for('home'))
    page = request.args.get('page', 1, type=int)
    users = User.query.filter_by(category = 'subadmin').filter_by(status = 'blocked').order_by(User.id.asc()).paginate(page = page, per_page = 5)
    return render_template("viewUsers.html", users = users, title = 'Blocked SubAdmins')


@app.route("/blockedUsersview")
@login_required
def blockedUsersView():
    if current_user.category != 'admin':
        return redirect(url_for('home'))
    page = request.args.get('page', 1, type=int)
    users = User.query.filter_by(category = 'user').filter_by(status = 'blocked').order_by(User.id.asc()).paginate(page = page, per_page = 5)
    return render_template("viewUsers.html", users = users, title = 'Blocked Users')

@app.route("/unblockUser/<int:id>", methods=['GET','POST'])
@login_required
def unblockUser(id):
    if current_user.category != 'admin':
        return redirect(url_for('home'))
    user = User.query.filter_by(id=id).first()
    userCat = user.category
    user.status = 'active'
    db.session.commit()
    if userCat == 'subadmin':
        return redirect(url_for('blockedSubAdminView'))
    else:
        return redirect(url_for('blockedUsersView'))

@app.route("/reserveUsername", methods=['GET', 'POST'])
@login_required
def reserveUsername():
    form = reserveForm()
    if current_user.category != 'admin':
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('reserveUsername.html', form=form, title='Reserve Username')
    if form.validate_on_submit():
        res_uname = ReservedUsername(res_username=form.res_username.data, reserved_for=form.reserved_for.data, linkedto = form.linkedto.data)
        db.session.add(res_uname)
        db.session.commit()
        flash(f'Username reserved succesfully', 'success')
    return render_template('reserveUsername.html', form=form, title='Reserve Username')

@app.route("/upload_csv", methods=['GET', 'POST'])
@login_required
def upload_csv():
    form = UploadcsvForm()
    if current_user.category != 'admin':
        return redirect(url_for('home'))
    if request.method == 'POST':
        csv_file = request.files['csv_file']
        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        if form.validate_on_submit():
            for row in csv_reader:
                res_user = ReservedUsername(res_username=row[0], reserved_for=row[1], linkedto=row[2])
                db.session.add(res_user)
                db.session.commit()
            flash(f'Successfully Imported Usernames','success')
            return redirect(url_for('viewReservedUsernames'))
    return render_template('uploadFilecsv.html', form = form, title = 'Import Usernames')

@app.route("/viewReservedUsernames")
@login_required
def viewReservedUsernames():
    if current_user.category != 'admin':
        return  redirect(url_for('home'))
    res_user = ReservedUsername.query.all()
    return render_template('viewResUser.html',  resUser = res_user, title = 'Reserved Usernames')



@app.route("/deleteResUsername/<int:id>", methods=['GET', 'POST'])
@login_required
def deleteResUsername(id):
    if current_user.category != 'admin':
        return redirect(url_for('home'))
    ReservedUsername.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Username Deleted','info')
    return redirect(url_for('viewReservedUsernames'))

@app.route("/suggestUsername/<int:id>", methods=['GET','POST'])
@login_required
def suggestUsername(id):
    if current_user.category != 'admin':
        return redirect(url_for('home'))
    if request.method == 'POST':
        sug_username = request.form['newUsername']
        msg = "Please change your current username! suggestion: " + sug_username 
        sender_id = current_user.id
        user = User.query.get(id)
        reciever_id = user.id
        notif = Notifications(recipient_userid = reciever_id, sender_userid = sender_id, notif_content = msg)
        db.session.add(notif)
        db.session.commit()
        flash(f'Suggestion sent to the user succesfully', 'success')
        return redirect(url_for('singleUserView',id = id))

@app.route("/editUsername/<int:id>", methods=['GET', 'POST'])
@login_required
def editUsername(id):
    if current_user.category != 'admin':
        return redirect(url_for('home'))
    if request.method == 'POST':
        new_username = request.form['newUsername']
        msg = "Your username is changed by admin! New username: " + new_username
        sender_id = current_user.id
        user = User.query.get(id)
        reciever_id = user.id
        user.username = new_username
        notif = Notifications(recipient_userid = reciever_id, sender_userid = sender_id, notif_content = msg)
        db.session.add(notif)
        db.session.commit()
        return redirect(url_for('singleUserView',id = id))

@app.route("/notificationView")
@login_required
def notificationView():
    user_id = current_user.id
    notifs = Notifications.query.filter_by(recipient_userid = user_id).order_by(Notifications.notif_date.desc()).all()
    return render_template('notificationView.html',notifs=notifs)