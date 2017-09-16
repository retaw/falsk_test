import redis



class Redishandler(object):
    PF_RECHARGE = "pf_lb_recharge"
    PF_GMCMD    = "pf_gw_gmcmd"

    TB_CLIENT_CUID_2_OPENID = "tb_client_cuid_2_openid"

    REDIS_AUTH_PASSWD = "111111"

    instance = None
    @staticmethod
    def me():
        if Redishandler.instance is None:
            Redishandler.instance = Redishandler()
        return Redishandler.instance

    def __init__(self):
        self.__conn = redis.StrictRedis(host='127.0.0.1', port=6379, password=Redishandler.REDIS_AUTH_PASSWD)

    def getConn(self):
        return self.__conn

    def playerExisit(self, playerid):
        return True #fortest
        return self.__conn.hexists(Redishandler.TB_CLIENT_CUID_2_OPENID, str(playerid))

    def playerRecharge(self, sn, playerid, money, operator):
        return self.playerExisit(playerid) and self.__conn.rpush(Redishandler.PF_RECHARGE, u"{},{},{},{}".format(sn, playerid, money, operator)) > 0

    def gmCmd(self, *gmcmd):
        gmcmdStr = u",".join(gmcmd)
        return self.__conn.rpush(Redishandler.PF_GMCMD, gmcmdStr) > 0

    def loadGameCfg(self):
        return self.gmCmd("reloadcfg")

if __name__ == '__main__':
    test()

