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
import wtforms_components

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
@main.route('/index')
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
    form.superviorid.data = current_user.agencyid
    if form.validate_on_submit():
        agencyid = form.agencyid.data
        superviorid = form.superviorid.data
        password = form.password.data
        if agencyid == superviorid:
            flash(u"代理的上级不能是自己")
        else:
            dbRet = Mysqlhandler.me().addAgency(agencyid, password, None if current_user.is_admin() else superviorid)
            if dbRet is None:
                form.agencyid.data = None
                form.superviorid.data = current_user.agencyid
                msg = u'代理设置成功, ID:{}, 上级ID:{}'.format(agencyid, superviorid)
                return render_template('form_ret.html', msg = msg, next_url = url_for('main.admin_add_agency'))
            flash(u"代理设置失败, {}".format(dbRet))
    return render_template('form.html', form=form, tittle=u"设置代理")


@main.route('/admin_modify_agency', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_modify_agency():
    form = ModifyAgencyForm()
    if form.validate_on_submit():
        agencyid = form.agencyid.data
        dbRet = Mysqlhandler.me().delAgency(agencyid)
        if dbRet is None:
            form.agencyid.data = ''
            msg = u"操作成功, {} 已经不是代理了".format(agencyid)
            return render_template('form_ret.html', msg = msg, next_url = url_for('main.admin_modify_agency'))
        flash(u"操作失败, {}".format(dbRet))
    return render_template('form.html', form=form, tittle=u"删除代理")


@main.route('/agency_recharge', methods=['GET', 'POST']) 
@login_required
def agency_recharge():
    form = AddAgencyMoneyForm()
    if form.validate_on_submit():
        agencyid = form.agencyid.data
        money    = form.money.data
        superviorid = current_user.agencyid

        if current_user.is_admin():
            dbRetIsOk, dbRetData = Mysqlhandler.me().agencyRechargeByAdmin(superviorid, agencyid, money)
        else:
            dbRetIsOk, dbRetData = Mysqlhandler.me().agencyRechargeBySupervior(superviorid, agencyid, money)
        if dbRetIsOk == True:
            form.agencyid.data = ""
            form.money.data = ""
            msg = u'代理充值成功, ID:{}, 充值额:{}, 流水号:{}'.format(agencyid, money, dbRetData)
            return render_template('form_ret.html', msg = msg, next_url = url_for('main.agency_recharge')) 
        
        flash(u"充值失败, {}".format(dbRetData))
    return render_template('form.html', form=form, tittle=u"给代理金库充值")


@main.route('/add_player', methods=['GET', 'POST']) 
@login_required
def add_player():
    form = AddPlayerForm()
    if not current_user.is_admin():
        form.superviorid.data = current_user.agencyid
        wtforms_components.read_only(form.superviorid)
    if form.validate_on_submit():
        playerid    = form.playerid.data
        superviorid = form.superviorid.data if current_user.is_admin() else current_user.agencyid #反外挂
        dbRetIsOk, dbRetData = Mysqlhandler.me().addPlayer(superviorid, playerid, current_user.is_admin())

        if dbRetIsOk == True:
            form.playerid.data    = ""
            form.superviorid.data = ""
            msg = u'玩家代理关系设置成功, 玩家ID:{}, 代理ID:{}'.format(playerid, superviorid)
            return render_template('form_ret.html', msg = msg, next_url = url_for('main.add_player')) 
        else:
            flash(u"绑定失败, {}".format(dbRetData))
    return render_template('form.html', form=form, tittle=u"设置玩家的代理")


@main.route('/player_recharge', methods=['GET', 'POST']) 
@login_required
def player_recharge():
    form = AddPlayerMoneyForm()
    if form.validate_on_submit():
        playerid = form.playerid.data
        money    = form.money.data

        agencyid = current_user.agencyid
        if current_user.is_admin():
            dbRetIsOk, dbRetData = Mysqlhandler.me().playerRechargeByAdmin(agencyid, playerid, money)
        else:
            dbRetIsOk, dbRetData = Mysqlhandler.me().playerRechargeByAgency(agencyid, playerid, money)

        if dbRetIsOk == True:
            form.playerid.data = ""
            form.money.data = ""
            msg = u'充值成功, 玩家id:{}, 充值额:{}, 流水号:{}'.format(playerid, money, dbRetData)
            return render_template('form_ret.html', msg = msg, next_url = url_for('main.player_recharge')) 
        else:
            flash(u"充值失败, {}".format(dbRetData))
    return render_template('form.html', form=form, tittle=u"给玩家游戏账号充值")



@main.route('/agency_financial_detail', methods=['GET', 'POST'])
@login_required
def agency_financial_detail():
    form = QueryAgencyFinancialForm()
    wtforms_components.read_only(form.submit2) #TODO, 暂时禁用, 待实现db中的指出查询后去掉这一行
    if not current_user.is_admin():
        form.agencyid.data = current_user.agencyid
        wtforms_components.read_only(form.agencyid)

    if form.validate_on_submit():
        agencyid = form.agencyid.data if current_user.is_admin() else current_user.agencyid #反外挂
        if form.submit1.data is True:
            info = u"钻石购买明细, 代理ID: {}".format(agencyid)
            dbRetIsOk, dbRetData =  Mysqlhandler.me().queryAgencyIncomeDetail(agencyid)
        else:
            info = u"钻石支出明细, 代理ID: {}".format(agencyid)
            dbRetIsOk, dbRetData =  Mysqlhandler.me().queryAgencyOutcomeDetail(agencyid)
        if dbRetIsOk == True:
            return render_template('financial_detail.html', info = info, records = dbRetData, next_url = url_for('main.agency_financial_detail'))
        flash(u"查询失败{}".format(dbRetData))
    return render_template('form.html', form=form, tittle=u"钻石明细查询")


@main.route('/agency_financial_info',  methods=['GET', 'POST'])
@login_required
def agency_financial_info():
    superviorid = None if current_user.is_admin() else current_user.agencyid
    form = QueryAgencyFinancialInfo()
    if form.validate_on_submit():
        if form.submit1.data is True:
            msg= u"下属累计购买钻石数量"
            dbRetIsOk, dbRetData = Mysqlhandler.me().queryAgencyIncomeInfo(superviorid)
        else:
            msg= u"下属累计支出钻石总量"
            dbRetIsOk, dbRetData = Mysqlhandler.me().queryAgencyOutcomeInfo(superviorid)
        if dbRetIsOk == True:
            return render_template('financial_info.html', msg = msg, records = dbRetData, next_url = url_for('main.agency_financial_info'))
        flash(u"查询失败, {}".format(dbRetData))
    return render_template('form.html', form=form, tittle=u"下属钻石情况查询")



@main.route('/player_financial_detail', methods=['GET', 'POST'])
@login_required
def player_financial_detail():
    pass
'''
    if current_user.is_admin():
        form = QueryPlayerFinancialByAdminForm()
        if form.validate_on_submit():
            agencyid = form.agencyid.data
            if agencyid is None or agencyid == "":
                agencyid = "*"
            playerid = form.playerid.data
            dbRetIsOk, dbRetData =  Mysqlhandler.me().queryPlayerRechargeDetail(playerid, agencyid)
            if dbRetIsOk == True:
                info = u"玩家充值明细查询, agencyid: {}  玩家id: {}".format(agencyid, playerid)
                return render_template('financial_detail.html', info = info, records = dbRetData, next_url = url_for('main.agency_financial_detail'))
            else:
                flash(u"查询失败{}".format(dbRetData))
        return render_template('form.html', form=form, tittle=u"玩家账目明细查询")
    else:
        form = QueryPlayerFinancialByAgencyForm()
        if form.validate_on_submit():
            agencyid = current_user.agencyid
            playerid = form.playerid.data
            dbRetIsOk, dbRetData =  Mysqlhandler.me().queryPlayerRechargeDetail(playerid, agencyid)
            if dbRetIsOk == True:
                info = u"玩家充值明细查询, agencyid: {}  玩家id: {}".format(agencyid, playerid)
                return render_template('financial_detail.html', info = info, records = dbRetData, next_url = url_for('main.agency_financial_detail'))
            else:
                flash(u"查询失败{}".format(dbRetData))
        return render_template('form.html', form=form, tittle=u"玩家账目明细查询")
'''


