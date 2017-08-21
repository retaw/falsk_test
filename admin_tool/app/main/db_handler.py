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

    def getAgencyBasicInfo(self, agencyid):
        cursor = self.getCursor()
        try:
            sql = u"select superviorid, passwd from agencies where agencyid = {}".format(agencyid)
            n = cursor.execute(sql)
            if n == 0:
                return None, None
            row = cursor.fetchone();
            return (row[0], row[1])
        except MySQLdb.Error as e:
            logger.error(e)
            raise
    

    def addAgency(self, agencyid, password, superviorid, isAdmin):
        if Redishandler.me().playerExisit(agencyid) is not True:
            return u"ID={}的玩家不存在".format(agencyid)
        cursor = self.getCursor()
        try:
            if isAdmin is not True:
                sqlCheckSuperviorid = u"select agencyid from agencies where agencyid={}".format(superviorid)
                if cursor.execute(sqlCheckSuperviorid) < 1:
                    return u"上级代理不正确, ID={}的代理不存在".format(superviorid)

            sqlTryInsertAgency = u"insert into agencies (agencyid) select {} from (select 1) as a where not exists(select agencyid from agencies where agencyid={}) limit 1".format(agencyid, agencyid)
            cursor.execute(sqlTryInsertAgency)

            sqlUpdateAgencyBasicInfo = u"update agencies set passwd='{}', superviorid={}  where agencyid={}".format(password, superviorid, agencyid)
            cursor.execute(sqlUpdateAgencyBasicInfo)

            self.commit(cursor)
        except MySQLdb.Error as e:
            logger.error(e)
            self.rollback(cursor)
            return e

    def delAgency(self, agencyid):
        cursor = self.getCursor()
        try:
            sql = u"delete from agencies where agencyid={}".format(agencyid)
            cursor.execute(sql)
            logger.info(u"delete agency, id={}".format(agencyid))
            self.commit(cursor)
        except MySQLdb.Error as e:
            logger.error(e)
            self.rollback(cursor)
            return e

    def agencyRechargeByAdmin(self, adminid, agencyid, money):
        cursor = self.getCursor()
        try:
            sqlCheckAgencyid = u"select agencyid from agencies where agencyid='{}'".format(agencyid)
            if cursor.execute(sqlCheckAgencyid) == 0:
                return False, u"代理 {} 不存在".format(agencyid)

            sqlInsertRecord = u"insert into agency_money (superviorid, agencyid, money) values ({}, {}, {})".format(adminid, agencyid, money)
            cursor.execute(sqlInsertRecord)

            sqlAddAgencyMoney     = u"update agencies set money = money + {} where agencyid = {}".format(money, agencyid)
            cursor.execute(sqlAddAgencyMoney)
            
            sqlGetSerialNum = "select last_insert_id()"
            cursor.execute(sqlGetSerialNum)
            row = cursor.fetchone()

            self.commit(cursor)
            return True, row[0]

        except MySQLdb.Error as e:
            logger.error(e)
            self.rollback(cursor)
            return False, e


    def agencyRechargeBySupervior(self, superviorid, agencyid, money):
        cursor = self.getCursor()
        try:
            sqlCheckAgencyRelation = u"select agencyid from agencies where superviorid={} and agencyid={}".format(superviorid, agencyid)
            if cursor.execute(sqlCheckAgencyRelation) == 0:
                return False, u"代理 {} 不是你的下级代理".format(agencyid)

            sqlDecSuperviorMoney = u"update agencies set money=money-{} where agencyid={} and money>={}".format(money, superviorid, money)
            if cursor.execute(sqlDecSuperviorMoney) == 0:
                return False, u"金库钻石不足"

            sqlIncAgencyMoney    = u"update agencies set money=money+{} where agencyid={}".format(money, agencyid)
            cursor.execute(sqlIncAgencyMoney)
            
            sqlInsertRecord = u"insert into agency_money (superviorid, agencyid, money) values ({}, {}, {})".format(superviorid, agencyid, money)
            cursor.execute(sqlInsertRecord)

            sqlGetSerialNum = "select last_insert_id()"
            cursor.execute(sqlGetSerialNum)
            row = cursor.fetchone()

            logger.info(u"代理充值给代理, superviorid={}, agencyid={}, money={}".format(superviorid, agencyid, money))
            self.commit(cursor)
            return True, row[0]

        except MySQLdb.Error as e:
            logger.error(e)
            self.rollback(cursor)
            return False, e


    def addPlayer(self, superviorid, playerid, isAdmin):
        cursor = self.getCursor()
        try:
            if isAdmin is True and superviorid == 0:
                sqlDeleteAgencyRelation = u"delete from players where playerid={}".format(playerid)
                cursor.execute(sqlCheckAgencyid)
                self.commit(cursor)
                return True, u"已解除玩家{}的现有代理关系".format(playerid)

            sqlCheckAgencyid = u"select agencyid from agencies where agencyid={}".format(superviorid)
            if cursor.execute(sqlCheckAgencyid) == 0:
                return False, u"代理 {} 不存在".format(superviorid)

            if isAdmin is not True:
                sqlCheckPlayerStatus = u"select superviorid from players where playerid={}".format(playerid)
                if cursor.execute(sqlCheckPlayerStatus) > 0: #已经有代理了
                    if cursor.fetchone()[0] == superviorid:
                        return False, u"玩家{}已经绑定你为代理, 不要重复绑定".format(playerid)
                    return False, u"玩家{}已经有代理了, 请找管理员进行更换代理操作".format(playerid)

            sqlTryInsertPlayer = u"insert into players (playerid) select {} from (select 1) as a where not exists(select playerid from players where playerid={}) limit 1".format(playerid, playerid)
            cursor.execute(sqlTryInsertPlayer)

            sqlUpdatePlayerBasicInfo = u"update players set superviorid={}, timestamp=current_timestamp".format(superviorid)
            cursor.execute(sqlUpdatePlayerBasicInfo)

            logger.info(u"设置玩家代理关系, playerid={}, agencyid={}".format(playerid, superviorid))
            self.commit(cursor)
            return True, u""

        except MySQLdb.Error as e:
            logger.error(e)
            self.rollback(cursor)
            return False, e


    def playerRechargeByAgency(self, agencyid, playerid, money):
        if Redishandler.me().playerExisit(playerid) is not True:
            return False, u"ID={}的玩家不存在".playerid
        cursor = self.getCursor()
        try:
            sqlCheckRelation = u"select playerid from players where playerid={} and superviorid={}".format(playerid, agencyid)
            if cursor.execute(sqlCheckRelation) == 0:
                return False, u"玩家{} 与你之间没有代理关系".format(playerid)

            sqlDecMoney = u"update agencies set money=money-{} where agencyid={} and money>={}".format(money, agencyid, money)
            if cursor.execute(sqlDecMoney) == 0:
                return False, u"金库钻石不足"

            sqlInsertRecord = u"insert into agency_money (superviorid, playerid, money) values ({}, {}, {})".format(agencyid, playerid, money)
            cursor.execute(sqlInsertRecord)

            sqlGetSerialNum = u"select last_insert_id()"
            cursor.execute(sqlGetSerialNum)
            sn = cursor.fetchone()[0]

            if Redishandler.me().playerRecharge(sn, playerid, money, agencyid) is not True:
                self.rollback(cursor)
                return False, u"unknown redis error"

            logger.info(u"player recharge by agency, sn={}, playerid={}, money={}, agencyid={}".format(sn, playerid, money, agencyid))
            self.commit(cursor)
            return True, sn

        except MySQLdb.Error as e:
            logger.error(e)
            self.rollback(cursor)
            return False, e
        except Exception as e:
            logger.error(e)
            self.rollback(cursor)
            raise


    def playerRechargeByAdmin(self, adminid, playerid, money):
        cursor = self.getCursor()
        try:
            sqlGetSerialNum = u"select last_insert_id()"
            cursor.execute(sqlGetSerialNum)
            sn = cursor.fetchone()[0]

            #add recharge record to redis
            if not Redishandler.me().playerExisit(playerid):
                return False, u"充值失败, 玩家id不存在"
            if Redishandler.me().playerRecharge(sn, playerid, money, adminid) is not True:
                self.rollback(cursor)
                return False, u"充值失败, 0x12"
            
            logger.info("player recharge by admin, sn={}, playerid={}, money={}, agencyid={}".format(sn, playerid, money, adminid))
            self.commit(cursor)
            return True, sn

        except MySQLdb.Error as e:
            logger.error(e)
            self.rollback(cursor)
        except Exception as e:
            logger.error(e)
            self.rollback(cursor)
            raise


    def queryAgencyIncomeInfo(self, superviorid = None):
        cursor = self.getCursor()
        try:
            sql = u"select agencyid, sum(money) from agency_money where agencyid is not null group by agencyid"
            if superviorid is not None:
                sql = (u"select b.agencyid, sum(b.money) from agencies as a, agency_money as b "
                        "where a.superviorid={} and a.agencyid=b.agencyid group by b.agencyid").format(superviorid)
            n = cursor.execute(sql)
            ret = []
            for row in cursor:
                ret.append((row[0], row[1]))

            print "queryAgencyIncomeInfo ok"
            return True, ret
        except MySQLdb.Error as e:
            print "queryAgencyIncomeInfo failed"
            logger.error(e)
            return False, e


    def queryAgencyOutcomeInfo(self, superviorid = None):
        cursor = self.getCursor()
        try:
            sql = u"select superviorid, sum(money) from agency_money group by superviorid"
            if superviorid is not None:
                sql = (u"select b.superviorid, sum(b.money) from agencies as a, agency_money as b "
                        "where a.superviorid=2  and a.agencyid=b.superviorid group by b.superviorid") .format(superviorid)
            n = cursor.execute(sql)
            ret = []
            for row in cursor:
                ret.append((row[0], row[1]))

            print "queryAgencyIncomeInfo ok"
            return True, ret
        except MySQLdb.Error as e:
            print "queryAgencyIncomeInfo failed"
            logger.error(e)
            return False, e


    def queryAgencyIncomeDetail(self, agencyid):
        cursor = self.getCursor();
        try:
            sql = u"select agencyid, money, superviorid, timestamp from agency_money where agencyid={}".format(agencyid)
            n = cursor.execute(sql)

            ret = []
            for row in cursor:
                ret.append((row[0], row[1], row[2], row[3].strftime("%Y-%m-%d %H:%M:%S")))
            return True, ret
        except MySQLdb.Error as e:
            logger.error(e)
            return False, e


    def queryAgencyOutcomeDetail(self, agencyid):
        cursor = self.getCursor();
        try:
            sql = u"select superviorid, money, agencyid, playerid, timestamp from agency_money where superviorid={}".format(agencyid)
            n = cursor.execute(sql)

            ret = []
            for row in cursor:
                ret.append((row[0], row[1], row[2], row[3], row[4].strftime("%Y-%m-%d %H:%M:%S")))
            return True, ret
        except MySQLdb.Error as e:
            logger.error(e)
            return False, e

'''
    def queryPlayerRechargeDetail(self, playerid, agencyid):
        cursor = self.getCursor();
        try:
            sql = u"select serial_num, money, agencyid, timestamp from agency_money where playerid={}".format(playerid)
            if agencyid != "*":
                sql += " and agencyid = {}".format(agencyid)
            n = cursor.execute(sql)

            ret = []
            for row in cursor:
                ret.append((str(row[0]), str(row[1]), str(row[2]), row[3].strftime("%Y-%m-%d %H:%M:%S")))
            return True, ret
        except MySQLdb.Error as e:
            logger.error(e)
            return False, e
'''














if __name__ == "__main__":
    hander = Mysqlhandler()
    hander.test()



