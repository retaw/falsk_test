# -*- coding: utf-8 -*-

#
# Author: water - waterlzj@gmail.com
#
# Last modified: 2017-08-08 09:19 +0800
#
# Description: 
#

from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, DateTimeField, IntegerField
from flask_admin.form.widgets import DatePickerWidget
from wtforms.validators import Required, Length, NumberRange, EqualTo, InputRequired
#from wtforms_components import TimeField



class AddAgencyForm(FlaskForm):
    agencyid      = IntegerField(u'代理ID(和游戏内的玩家ID相同)', validators=[Required()])
    superviorid   = IntegerField(u'上级ID(无上级代理的这里填88888888)', validators=[InputRequired()], default=88888888)
    password      = PasswordField(u'密码', validators=[Required(), EqualTo("passwordAgain", message=u"两次输入的密码必须一致")])
    passwordAgain = PasswordField(u'再输一遍密码', validators=[Required()])
    submit = SubmitField(u'确定')


class ModifyAgencyForm(FlaskForm):
    agencyid    = IntegerField(u'代理ID', validators=[Required()])
    submit = SubmitField(u'确定')


class AddAgencyMoneyForm(FlaskForm):
    agencyid    = IntegerField(u"代理ID", validators=[Required()])
    money       = IntegerField(u"钻石",   validators=[Required(), NumberRange(min = 1)])
    submit = SubmitField(u'确定')
    

class AddPlayerForm(FlaskForm):
    playerid    = IntegerField(u'玩家ID', validators=[Required()])
    superviorid = IntegerField(u'代理ID(填0表示不属于任何代理)', validators=[InputRequired()])
    submit = SubmitField(u'确定')


class AddPlayerMoneyForm(FlaskForm):
    playerid    = IntegerField(u"玩家ID", validators=[Required()])
    money       = IntegerField(u"钻石",      validators=[Required(), NumberRange(min = 1)])
    submit = SubmitField(u'确定')


class QueryAgencyFinancialForm(FlaskForm):
    agencyid    = IntegerField(u"代理ID", validators=[Required()])
    submit1 = SubmitField(u"购钻明细")
    submit2 = SubmitField(u"支钻明细")
    pass


class QueryAgencyFinancialInfoForm(FlaskForm):
    submit1 = SubmitField(u"下属购买钻石查询")
    submit2 = SubmitField(u"下属支出钻石查询")


class ModifyPasswordForm(FlaskForm):
    password         = PasswordField(u'当前密码', validators=[Required()])
    newpassword      = PasswordField(u'新密码', validators=[Required(), EqualTo("newpasswordAgain", message=u"两次输入的密码必须一致")])
    newpasswordAgain = PasswordField(u'再输一遍新密码', validators=[Required()])
    submit = SubmitField(u'确定')


'''
class QueryPlayerFinancialByAdminForm(FlaskForm):
    playerid    = IntegerField(u"玩家ID", validators=[Required()])
    agencyid    = IntegerField(u"代理ID", validators=[])
    submit = SubmitField(u"确定")
    pass


class QueryPlayerFinancialByAgencyForm(FlaskForm):
    playerid    = IntegerField(u"玩家ID", validators=[Required()])
    submit = SubmitField(u"确定")
    pass
'''
