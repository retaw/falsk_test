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
from wtforms.validators import Required, Length, NumberRange, EqualTo



class AddAgencyForm(FlaskForm):
    phonenum = StringField(u'手机', validators=[Required()])
    nickname = StringField(u'名字', validators=[Required()])
    password = PasswordField(u'密码', validators=[Required(), EqualTo("passwordAgain", message=u"两次输入的密码必须一致")])
    passwordAgain = PasswordField(u'再输一遍密码', validators=[Required()])
    submit = SubmitField(u'确定')


class AddAgencyMoneyForm(FlaskForm):
    phonenum    = StringField(u"代理手机号", validators=[Required()])
    money       = IntegerField(u"金额",      validators=[Required(), NumberRange(min = 1)])
    submit = SubmitField(u'确定')
    

class AddPlayerMoneyForm(FlaskForm):
    playerid    = StringField(u"玩家ID", validators=[Required()])
    money       = IntegerField(u"金额",      validators=[Required(), NumberRange(min = 1)])
    submit = SubmitField(u'确定')


class QueryAgencyFinancialBySelfForm(FlaskForm):
    submit = SubmitField(u"确定")
    pass

class QueryAgencyFinancialByAdminForm(FlaskForm):
    phonenum    = StringField(u"代理手机号", validators=[Required()])
    submit = SubmitField(u"确定")
    pass

class QueryPlayerFinancialByAdminForm(FlaskForm):
    playerid    = StringField(u"玩家ID", validators=[Required()])
    phonenum    = StringField(u"代理手机号", validators=[])
    submit = SubmitField(u"确定")
    pass

class QueryPlayerFinancialByAgencyForm(FlaskForm):
    playerid    = StringField(u"玩家ID", validators=[Required()])
    submit = SubmitField(u"确定")
    pass
