from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from main.db_handler import Mysqlhandler
import json



class User(UserMixin):
    admin_agencyid = 88888888
    admin_password = "mcnxs_052"


    @staticmethod
    def create(agencyid):
        print "agenceid = ", agencyid
        password = User.admin_password if agencyid == User.admin_agencyid else "123456"
        superviorid = None
        money = 0
        if agencyid != User.admin_agencyid:
            superviorid, password, money = Mysqlhandler.me().getAgencyBasicInfo(agencyid)
        else:
            print "admin login"
        if password is not None:
            return User(agencyid, superviorid, password, money)
        return None

    def __init__(self, agencyid, superviorid, password, money):
        self.agencyid    = agencyid
        self.superviorid = superviorid
        self.password    = password
        self.money       = money

    def get_id(self):
        return str(self.agencyid)

    def refreshFromDb(self):
        if self.is_admin():
            return
        self.superviorid, self.password, self.money = Mysqlhandler.me().getAgencyBasicInfo(self.agencyid)
        print "refresh from db"

    def verify_password(self, password):
        print "verify_passwd {} {}".format(self.agencyid, password)
        return password == self.password

    def is_admin(self):
        return self.agencyid == User.admin_agencyid

    def __repr__(self):
        return '<User %r>' % self.agencyid



@login_manager.user_loader
def load_user(agencyidStr):
    print "load_user", agencyidStr
    return User.create(int(agencyidStr))



