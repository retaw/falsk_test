# -*- coding: utf-8 -*-

#
# Author: water - waterlzj@gmail.com
#
# Last modified: 2017-08-08 07:30 +0800
#
# Description: 
#

import sys 
import MySQLdb
from redis_handler import Redishandler
#import IniParser

#import contextlib import closing

import logging
logger = logging.getLogger()

class Mysqlhandler:
    instance = None
    @staticmethod
    def me():
        if Mysqlhandler.instance is None:
            Mysqlhandler.instance = Mysqlhandler()
        return Mysqlhandler.instance
        

    def __init__(self):
        self.__conn = None
        self.connect()

    def connect(self):
#        reload(sys) 
#        sys.setdefaultencoding('utf-8') 

        try:
            #cfgPath = "../config/db_mysql.cfg"
            #config = IniParser.IniFile(cfgPath)
    
            #host = config.get("db", "host")
            #port = config.get("db", "port")
            #db = config.get("db", "dbname")
            #user = config.get("authorized", "username")
            #pwd = config.get("authorized", "password")

            host = "127.0.0.1"
            port = "3306"
            db   = "game"
            user = "water"
            pwd  = "111111"

            print "dbinfo:",host,port,db,user,pwd
    
            self.__conn = MySQLdb.connect(
                    host = host,
                    port = int(port),
                    db = db, 
                    user = user,
                    passwd = pwd,
                    charset = "utf8",
                    connect_timeout = 10) 
        except MySQLdb.Error as e:
            logger.error(e)
            raise
        return

    #########################################
    def getCursor(self):
        try:
            ret = self.__conn.ping()
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
        return self.__conn.cursor()

    #########################################
    def commit(self, cursor):
        cursor.close()
        self.__conn.commit()

    #########################################
    def rollback(self, cursor):
        self.__conn.rollback()
        cursor.close()



######################game logic#####################
    def test(self):
        cursor = self.getCursor()

    def getAgencyPassword(self, phonenum):
        cursor = self.getCursor()
        try:
            sql = u"select passwd from agencies where phonenum = '{}'".format(phonenum)
            n = cursor.execute(sql)
            if n == 0:
                return None
            row = cursor.fetchone();
            return row[0]
        except MySQLdb.Error as e:
            logger.error(e)
            raise
    

    def addAgency(self, phonenum, nickname, password):
        cursor = self.getCursor()
        try:
            sqlTryInsert = u"insert into agencies (phonenum) select '{}' from (select 1) as a where not exists(select phonenum from agencies where phonenum = '{}') limit 1".format(phonenum, phonenum)
            n = cursor.execute(sqlTryInsert);
            if n > 0:
                sqlUpdatePasswd = u"update agencies set passwd = '{}', nickname='{}' where phonenum = '{}'".format(password, nickname, phonenum)
                cursor.execute(sqlUpdatePasswd)
            self.commit(cursor)
        except MySQLdb.Error as e:
            logger.error(e)
            self.rollback(cursor)
            return e



    def agencyRecharge(self, phonenum, money):
        cursor = self.getCursor()
        try:
            sqlCheckPhonenum = u"select phonenum from agencies where phonenum = '{}'".format(phonenum)
            if cursor.execute(sqlCheckPhonenum) == 0:
                return False, u"代理 {} 不存在".format(phonenum)

            sqlInsertRecord = u"insert into agency_money (phonenum, money, playerid) values ('{}', {}, 0)".format(phonenum, money)
            cursor.execute(sqlInsertRecord)

            sqlAddMoney     = u"update agencies set money = money + {} where phonenum = {}".format(money, phonenum)
            cursor.execute(sqlAddMoney)
            
            sqlGetSerialNum = "select last_insert_id()"
            cursor.execute(sqlGetSerialNum)
            row = cursor.fetchone()

            self.commit(cursor)
            return True, row[0]

        except MySQLdb.Error as e:
            logger.error(e)
            self.rollback(cursor)
            return False, e


    def playerRechargeByAgency(self, phonenum, playerid, money):
        if Redishandler.me().playerExisit(playerid) is not True:
            return False, u"ID={}的玩家不存在"
        cursor = self.getCursor()
        try:
            sqlSelectAgencyMoney = u"select money from agencies where phonenum = {}".format(phonenum);
            n = cursor.execute(sqlSelectAgencyMoney)
            if n != 1:
                return False, u"充值失败, 0x11"
            agencyMoney = cursor.fetchone()[0]
            if agencyMoney < money:
                return False, u"余额不足, 无法给玩家充值, 当前余额{}".format(agencyMoney)

            sqlInsertRecord = u"insert into agency_money (phonenum, money, playerid) values ('{}', {}, {})".format(phonenum, -money, playerid)
            cursor.execute(sqlInsertRecord)

            sqlReduceMoney  = u"update agencies set money = money - {} where phonenum = {}".format(money, phonenum)
            cursor.execute(sqlReduceMoney)

            sqlGetSerialNum = "select last_insert_id()"
            cursor.execute(sqlGetSerialNum)
            sn = cursor.fetchone()[0]

            #add recharge record to redis
            if not Redishandler.me().playerExisit(playerid):
                return False, u"充值失败, 玩家id不存在"
            if Redishandler.me().playerRecharge(sn, playerid, money, phonenum) is not True:
                self.rollback(cursor)
                return False, u"充值失败, 0x12"

            self.commit(cursor)
            logger.log("player recharge by agency, sn={}, playerid={}, money={}, phonenum={}".format(sn, playerid, money, phonenum))
            return True, sn

        except MySQLdb.Error as e:
            logger.error(e)
            self.rollback(cursor)
            return False, e
        except Exception as e:
            logger.error(e)
            self.rollback(cursor)
            raise



    def playerRechargeByAdmin(self, playerid, money):
        phonenum = '88888888'
        cursor = self.getCursor()
        try:
            sqlInsertRecord = u"insert into agency_money (phonenum, money, playerid) values ({}, {}, {})".format(phonenum, -money, playerid)
            cursor.execute(sqlInsertRecord)

            sqlReduceMoney  = u"update agencies set money = money - {} where phonenum = {}".format(money, phonenum)
            cursor.execute(sqlReduceMoney)

            sqlGetSerialNum = "select last_insert_id()"
            cursor.execute(sqlGetSerialNum)
            sn = cursor.fetchone()[0]

            #add recharge record to redis
            if not Redishandler.me().playerExisit(playerid):
                return False, u"充值失败, 玩家id不存在"
            if Redishandler.me().playerRecharge(sn, playerid, money, phonenum) is not True:
                self.rollback(cursor)
                return False, u"充值失败, 0x12"
            
            self.commit(cursor)
            logger.log("player recharge by admin, sn={}, playerid={}, money={}, phonenum={}".format(sn, playerid, money, phonenum))
            return True, sn

        except MySQLdb.Error as e:
            logger.error(e)
            self.rollback(cursor)
        except Exception as e:
            logger.error(e)
            self.rollback(cursor)
            raise

    def queryAgencyFinancialDetail(self, phonenum):
        cursor = self.getCursor();
        try:
            sql = u"select serial_num, money, playerid, timestamp from agency_money where phonenum={}".format(phonenum)
            n = cursor.execute(sql)

            ret = []
            for row in cursor:
                ret.append((str(row[0]), str(row[1]), str(row[2]), row[3].strftime("%Y-%m-%d %H:%M:%S")))
            return True, ret
        except MySQLdb.Error as e:
            logger.error(e)
            return False, e

    def queryPlayerRechargeDetail(self, playerid, phonenum):
        cursor = self.getCursor();
        try:
            sql = u"select serial_num, money, phonenum, timestamp from agency_money where playerid={}".format(playerid)
            if phonenum != "*":
                sql += " and phonenum = {}".format(phonenum)
            n = cursor.execute(sql)

            ret = []
            for row in cursor:
                ret.append((str(row[0]), str(row[1]), str(row[2]), row[3].strftime("%Y-%m-%d %H:%M:%S")))
            return True, ret
        except MySQLdb.Error as e:
            logger.error(e)
            return False, e












































if __name__ == "__main__":
    hander = Mysqlhandler()
    hander.test()



