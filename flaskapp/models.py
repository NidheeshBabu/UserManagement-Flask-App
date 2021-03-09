

from flaskapp import db, app, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    category = db.Column(db.String(10), default='user')
    status = db.Column(db.String(10), default='active')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.category}', '{self.status}')"

class ReservedUsername(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    res_username = db.Column(db.String(20), unique=True, nullable=False)
    reserved_for = db.Column(db.String(20), nullable=False, default='N/A')
    modified_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    linkedto = db.Column(db.String(20), default='notlinked')

    def __repr__(self):
        return f"ReservedUsername('{self.res_username}', '{self.reserved_for}','{self.modified_on}','{self.linkedto}')"

class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    recipient_userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    sender_userid =  db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    notif_content = db.Column(db.Text, nullable = False)
    notif_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Notifications('{self.recipient_userid}', '{self.sender_userid}', '{self.notif_date}')"