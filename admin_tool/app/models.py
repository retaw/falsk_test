from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from main.db_handler import Mysqlhandler
import json



class User(UserMixin):
    admin_agencyid = 88888888
    admin_password = "mcnxs_052"

    viceadmin1_agencyid = 88887777
    viceadmin1_password = "dcjz1%b"

    viceadmin2_agencyid = 88886666
    viceadmin2_password = "xycap1d="

    @staticmethod
    def create(agencyid):
        print "agenceid = ", agencyid
        superviorid = None
        money = 0
        if agencyid == User.admin_agencyid:
            password = User.admin_password 
            print "admin login"
        elif agencyid == User.viceadmin1_agencyid:
            password = User.viceadmin1_password
            print "viceadmin login"
        elif agencyid == User.viceadmin2_agencyid:
            password = User.viceadmin2_password
            print "viceadmin login"
        else:
            superviorid, password, money = Mysqlhandler.me().getAgencyBasicInfo(agencyid)
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

    def adminid(self):
        return User.admin_agencyid

    def refreshFromDb(self):
        if self.is_admin():
            return
        self.superviorid, self.password, self.money = Mysqlhandler.me().getAgencyBasicInfo(self.agencyid)
        print "refresh from db"

    def verify_password(self, password):
        print "verify_passwd {} {} {}".format(self.agencyid, self.password, password)
        return password == self.password

    def is_admin(self):
        return self.agencyid == User.admin_agencyid

    def is_viceadmin(self):
        return self.agencyid == User.viceadmin1_agencyid or  self.agencyid == User.viceadmin2_agencyid

    def is_staff(self):
        return self.is_viceadmin() or self.is_admin()

    def __repr__(self):
        return '<User %r>' % self.agencyid



@login_manager.user_loader
def load_user(agencyidStr):
    print "load_user", agencyidStr
    return User.create(int(agencyidStr))



