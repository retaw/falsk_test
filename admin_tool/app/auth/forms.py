# -*- coding: utf-8 -*-

#
# Author: water - waterlzj@gmail.com
#
# Last modified: 2017-07-22 23:16 +0800
#
# Description: 
#
from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, DateTimeField, IntegerField
from flask_admin.form.widgets import DatePickerWidget
from wtforms.validators import Required, Length, Email, InputRequired


class LoginForm(FlaskForm):
    agencyid = IntegerField(u'账号(ID)', validators=[InputRequired()])
    password = PasswordField(u'密码', validators=[Required()])
    #date1     = DateTimeField(u'start', widget=DatePickerWidget())
    #remember_me = BooleanField(u'保持登入')
    submit = SubmitField(u'登录')
