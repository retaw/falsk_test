from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from main.db_handler import Mysqlhandler
import json



class User(UserMixin):
    admin_phonenum = "88888888"
    admin_password = "123456"


    @staticmethod
    def create(phonenum):
        password = "123456"
        if phonenum != User.admin_phonenum:
            password = Mysqlhandler.me().getAgencyPassword(phonenum)
        if password is not None:
            return User(phonenum, password)
        return None

    def __init__(self, phonenum, password):
        self.phonenum = phonenum
        self.password = password

    def get_id(self):
        return self.phonenum

    def verify_password(self, password):
        print "verify_passwd {} {}".format(self.phonenum, password)
        return password == self.password

    def is_admin(self):
        return self.phonenum == User.admin_phonenum

    def __repr__(self):
        return '<User %r>' % self.username



@login_manager.user_loader
def load_user(phonenum):
    print "load_user", phonenum
    return User.create(phonenum)



