# -*- coding: utf-8 -*-

#
# Author: water - waterlzj@gmail.com
#
# Last modified: 2017-07-23 18:43 +0800
#
# Description: 
#


from flask import render_template, abort, redirect, request, url_for, flash
from flask_login import login_required, current_user
from . import main
from functools import wraps
from db_handler import Mysqlhandler
from .forms import *

def admin_required(func):
    @wraps(func)
    def decorated_admin(*args, **kwargs):
        if current_user.is_admin():
            return func(*args, **kwargs)
        else:
            flash(u'权限不足')
            return redirect(request.args.get('next') or url_for('main.index'))
    return decorated_admin



@main.route('/')
def index():
    return render_template('index.html')

@main.route('/admin_test')
@login_required
@admin_required
def admin_test():
    return u'暂未开放'

@main.route('/admin_add_agency',  methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_agency():
    form = AddAgencyForm()
    if form.validate_on_submit():
        phonenum = form.phonenum.data
        nickname = form.nickname.data
        password = form.password.data
        dbRet = Mysqlhandler.me().addAgency(phonenum, nickname, password)
        if dbRet is None:
            form.phonenum.data = ""
            form.nickname.data = ""
            msg = u'添加成功, 手机:{}, 名字:{}'.format(phonenum, nickname)
            return render_template('form_ret.html', msg = msg, next_url = url_for('main.admin_add_agency'))
        else:
            flash(u"添加失败, 数据库写入失败, {}".format(dbRet))
    return render_template('form.html', form=form, tittle=u"添加代理")


@main.route('/admin_agency_recharge', methods=['GET', 'POST']) 
@login_required
@admin_required
def admin_agency_recharge():
    form = AddAgencyMoneyForm()
    if form.validate_on_submit():
        phonenum = form.phonenum.data
        money    = form.money.data
        dbRetIsOk, dbRetData = Mysqlhandler.me().agencyRecharge(phonenum, money)
        if dbRetIsOk == True:
            form.phonenum.data = ""
            form.money.data = ""
            msg = u'代理充值成功, 手机:{}, 充值金额:{}, 流水号:{}'.format(phonenum, money, dbRetData)
            return render_template('form_ret.html', msg = msg, next_url = url_for('main.admin_agency_recharge')) 
        else:
            flash(u"充值失败, {}".format(dbRetData))
    return render_template('form.html', form=form, tittle=u"代理充值")


@main.route('/player_recharge', methods=['GET', 'POST']) 
@login_required
def player_recharge():
    form = AddPlayerMoneyForm()
    if form.validate_on_submit():
        playerid = form.playerid.data
        money    = form.money.data

        if current_user.is_admin():
            dbRetIsOk, dbRetData = Mysqlhandler.me().playerRechargeByAdmin(playerid, money)
        else:
            phonenum = current_user.phonenum
            dbRetIsOk, dbRetData = Mysqlhandler.me().playerRechargeByAgency(phonenum, playerid, money)

        if dbRetIsOk == True:
            form.playerid.data = ""
            form.money.data = ""
            msg = u'充值成功, 玩家id:{}, 充值金额:{}, 流水号:{}'.format(playerid, money, dbRetData)
            return render_template('form_ret.html', msg = msg, next_url = url_for('main.player_recharge')) 
        else:
            flash(u"充值失败, {}".format(dbRetData))
    return render_template('form.html', form=form, tittle=u"玩家充值")



@main.route('/agency_financial_detail', methods=['GET', 'POST'])
@login_required
def agency_financial_detail():
    if current_user.is_admin():
        form = QueryAgencyFinancialByAdminForm()
        if form.validate_on_submit():
            phonenum = form.phonenum.data
            dbRetIsOk, dbRetData =  Mysqlhandler.me().queryAgencyFinancialDetail(phonenum)
            if dbRetIsOk == True:
                info = "代理资金明细查询, 代理手机号: {}".format(phonenum)
                return render_template('financial_detail.html', info = info, records = dbRetData, next_url = url_for('main.agency_financial_detail'))
            else:
                flash(u"查询失败{}".format(dbRetData))
        return render_template('form.html', form=form, tittle=u"代理账目明细查询")
    else:
        form = QueryAgencyFinancialBySelfForm()
        if form.validate_on_submit():
            phonenum = current_user.phonenum
            dbRetIsOk, dbRetData =  Mysqlhandler.me().queryAgencyFinancialDetail(phonenum)
            if dbRetIsOk == True:
                info = "代理资金明细查询, 代理手机号: {}".format(phonenum)
                return render_template('financial_detail.html', info = info, records = dbRetData, next_url = url_for('main.agency_financial_detail'))
            else:
                flash(u"查询失败{}".format(dbRetData))
        return render_template('form.html', form=form, tittle=u"个人账目明细查询")
            


@main.route('/player_financial_detail', methods=['GET', 'POST'])
@login_required
def player_financial_detail():
    if current_user.is_admin():
        form = QueryPlayerFinancialByAdminForm()
        if form.validate_on_submit():
            phonenum = form.phonenum.data
            if phonenum is None or phonenum == "":
                phonenum = "*"
            playerid = form.playerid.data
            dbRetIsOk, dbRetData =  Mysqlhandler.me().queryPlayerRechargeDetail(playerid, phonenum)
            if dbRetIsOk == True:
                info = u"玩家充值明细查询, 代理手机号: {}  玩家id: {}".format(phonenum, playerid)
                return render_template('financial_detail.html', info = info, records = dbRetData, next_url = url_for('main.agency_financial_detail'))
            else:
                flash(u"查询失败{}".format(dbRetData))
        return render_template('form.html', form=form, tittle=u"玩家账目明细查询")
    else:
        form = QueryPlayerFinancialByAgencyForm()
        if form.validate_on_submit():
            phonenum = current_user.phonenum
            playerid = form.playerid.data
            dbRetIsOk, dbRetData =  Mysqlhandler.me().queryPlayerRechargeDetail(playerid, phonenum)
            if dbRetIsOk == True:
                info = u"玩家充值明细查询, 代理手机号: {}  玩家id: {}".format(phonenum, playerid)
                return render_template('financial_detail.html', info = info, records = dbRetData, next_url = url_for('main.agency_financial_detail'))
            else:
                flash(u"查询失败{}".format(dbRetData))
        return render_template('form.html', form=form, tittle=u"玩家账目明细查询")




