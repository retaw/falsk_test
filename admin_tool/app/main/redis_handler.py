import redis
import config



class Redishandler(object):
    PF_RECHARGE = "pf_lb_recharge"
    PF_GW_GMCMD    = "pf_gw_gmcmd"
    PF_LB_GMCMD    = "pf_lb_gmcmd"

    TB_CLIENT_CUID_2_OPENID = "tb_client_cuid_2_openid"

    host   = config.redis["host"]
    port   = config.redis["port"]
    passwd = config.redis["pwd"]

    instance = None
    @staticmethod
    def me():
        if Redishandler.instance is None:
            Redishandler.instance = Redishandler()
        return Redishandler.instance

    def __init__(self):
        self.__conn = redis.StrictRedis(host=Redishandler.host, port=Redishandler.port, password=Redishandler.passwd)

    def getConn(self):
        return self.__conn

    def playerExisit(self, playerid):
        return True #fortest
        return self.__conn.hexists(Redishandler.TB_CLIENT_CUID_2_OPENID, str(playerid))

    def playerRecharge(self, sn, playerid, money, operator):
        return self.playerExisit(playerid) and self.__conn.rpush(Redishandler.PF_RECHARGE, u"{},{},{},{}".format(sn, playerid, money, operator)) > 0

    def gmCmdGw(self, *gmcmd):
        gmcmdStr = u",".join(gmcmd)
        return self.__conn.rpush(Redishandler.PF_GW_GMCMD, gmcmdStr) > 0

    def gmCmdLb(self, *gmcmd):
        gmcmdStr = u",".join(gmcmd)
        return self.__conn.rpush(Redishandler.PF_LB_GMCMD, gmcmdStr) > 0

    def loadGameCfg(self):
        return self.gmCmdGw("reloadcfg")

    def dismissRoom(self, roomid, ownerid):
        return self.gmCmdLb("dismissroom", str(roomid), str(ownerid))

if __name__ == '__main__':
    test()

