# -*- coding: utf-8 -*-

#
# Author: water - waterlzj@gmail.com
#
# Last modified: 2016-11-12 20:41 +0800
#
# Description:  tcp长连接服务器，用于接收worker进程的数据库操作请求
#               仅服务于少数几个worker进程, 故使用select效率足够了
#


# Msg Structer:


from Queue import Queue
import time
import select
import socket
import gm_pb2 as message
from google import protobuf

import sys
sys.path.append("..")
from logger import logger


class TcpPacket(object):
    HEADER_LEN = 4
    def __init__(self):
        self.buf = ""
        self.header = ""
        self.body   = ""

    def ready(self):
        bufLen = len(self.buf)
        if bufLen < TcpPacket.HEADER_LEN:
            return False
        bodyLen = struct.unpack("=i", self.buf)
        return bodyLen + Messge.HEADER_LEN == bufLen

    def resetLen(self):
        bufLen = len(self.buf)
        if bufLen < TcpPacket.HEADER_LEN:
            return TcpPacket.HEADER_LEN - bufLen
        bodyLen = struct.unpack("=i", self.buf)[0]
        return bodyLen + Messge.HEADER_LEN - bufLen

    def append(self, data):
        self.buf = self.buf + data

    def data(self):
        return self.buf, len(self.buf)

    def popfront(self, size):
        self.buf = self.buf[size:]

    def msgData(self):
        if not self.ready():
            return 0, None
        return struct.unpack(self.buf[4:4]), self.buf[8:]
        


class Client(object):
    NORMAL = 0
    CLOSED = 1
    ERROR  = 2
    def __init__(self, sckt, remoteAddr):
        self.status = Client.NORMAL
        self.sckt = sckt
        self.remoteAddr = remoteAddr
        self.sendQueue = Queue()
        self.recvbuf = TcpPacket()
        self.sendbuf = None

    def handMsg(self):
        if not self.recvbuf.ready():
            return
        
        packet = self.recvbuf
        self.recvbuf = TcpPacket()

        msgCode, msgBin = packet.msgData()
#       descriptor = protobuf.reflection.GeneratedProtocolMessageType.
        
        if msgCode == 1073741828:
            msg = message.AddMoney()
            msg.ParseFromString(msgBin)
            print msg.money1
        else:
            print "invalid msgCode, {}".format(msgCode)


    def tryRecv(self):
        if self.status != Client.NORMAL:
            return

        while True:
            if self.recvbuf.ready:
                break
            try:
                restLen = self.recvbuf.restLen()
                newData = self.sckt.recv(restLen)
                recvLen = len(newData)

                #对方已关闭
                if recvLen == 0:
                    self.sckt.close()
                    self.status = Client.CLOSED
                    break

                self.recvbuf.append(newData)
            except socket.error, e:
                errNum = e.args[0]
                if not (errNum == errno.EAGAIN or errNum == errno.EWOULDBLOCK):
                    print "recv error: ", e
                    self.status = ERROR
                    break
        return

    def trySend(self, TcpPacket = None):
        if TcpPacket is not None:
            self.sendQueue.put(TcpPacket)

        if self.sendbuf is None and not self.sendQueue.empty():
            self.sendbuf = self.sendQueue.get()

        while self.sendbuf is not None:
            data, dataLen = self.sendbuf.data()
            sendLen = self.sckt.send(data)

            if sendLen < dataLen:
                self.sendbuf.popfront(sendLen)
                break;

            if not self.sendQueue.empty():
                self.sendbuf = self.sendQueue.get()
            else:
                self.sendbuf = None
        return
        


class Server(object):
    def __init__(self):
        self.listenSckt = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	self.listenSckt.setblocking(False)
	self.listenSckt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR  , 1)
        self.listenSckt.bind(("127.0.0.1", 10001))
	self.listenSckt.listen(10)

        self.clients = {}
 
        
        self.readSckts = [self.listenSckt]
        self.writeSckts = []

        self.recvMsgQueue = Queue(maxsize = 10000)
        self.sendMsgQueues = {}


    def loop(self):
        while True:
            readable, writable, exceptional = select.select(self.readSckts, self.writeSckts, self.readSckts, 0)
            #print "after select"
            for sckt in readable:
                if sckt is self.listenSckt:
                    connSckt, remoteAddr = self.listenSckt.accept()
                    print "new conn from: ", remoteAddr
                    connSckt.setblocking(False)
                    self.readSckts.append(connSckt)
                    self.writeSckts.append(connSckt)
                    self.clients[connSckt] = Client(sckt, remoteAddr)
                else:
                    client = self.clients[sckt]
                    client.tryRecv()
            for sckt in writable:
                client = self.clients[sckt]
                client.trySend()

            for sckt, client in self.clients.iteritems():
                client.handMsg()

            time.sleep(0.1)
        return

def main():
    s = Server();
    s.loop()

if __name__ == '__main__':
    from gevent import monkey
    monkey.patch_all()
    main()

