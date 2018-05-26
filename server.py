import asyncio
import os
import logging
from PyQt5.QtCore import *
# PYTHONASYNCIODEBUG=1
# logging.basicConfig(level=logging.DEBUG)
class FTPServer(QObject):
    begin = pyqtSignal()
    stop = pyqtSignal()
    onconnect = pyqtSignal(str,str)
    upload = pyqtSignal(str)
    download = pyqtSignal(str)
    disconnect = pyqtSignal(str,str)
    def __init__(self, host="0.0.0.0", port=21, parent=None,whitelist=[],blacklist=[],username_info = [],timeout=60.0,maxcon = 0):
        super(FTPServer, self).__init__(parent)
        self.maxcon = maxcon
        self.con = 0
        self.whitelist = whitelist
        self.blacklist = blacklist
        self.timeout = timeout
        self.loop = asyncio.new_event_loop()
        self.cond = asyncio.Condition(loop=self.loop)
        asyncio.set_event_loop(self.loop)
        self.username_info = username_info
        self.command_list = {
            "USER": "user",
            "CWD": "cwd",
            "PASV": "pasv",
            "LIST": "list",
            "PASS": "password",
            "QUIT": "quit",
            "PORT": "port",
            "TYPE": "type",
            "MODE": "mode",
            "STRU": "stru",
            "RETR": "retr",
            "STOR": "stor",
            "NOOP": "noop",
            "PWD": "pwd",
            "MKD": "mkd",
            "QUIT:":"quit"
            }
        self.addr = ""
        self.host = host
        self.port = port
        self.username = None
        self.message = None
        self.rootpath = './'
        self.path = '/'
        self.dtp_loop = asyncio.new_event_loop()
        self.ports = [port for port in range(10000, 10100)]
        self.available_port = None
        self.data_ports = asyncio.Queue(loop=self.loop)
        for data_port in self.ports:
            self.data_ports.put_nowait(data_port)
    async def handle_echo(self, reader, writer):
        self.reader = reader
        self.writer = writer
        data = "220 welcome.\r\n".encode()
        print(data)
        self.writer.write(data)
        self.addr = self.writer.get_extra_info('peername')
        self.host = self.writer.get_extra_info('sockname')
        self.con = self.con + 1
        if self.ip_handle(self.addr[0]):
            await self.writer.drain()
            while True:
                if self.maxcon != 0:
                    if self.con > self.maxcon:
                        print("reach max cons")
                        self.writer.close()
                        self.disconnect.emit(self.username, self.addr[0])
                        break
                try:
                    data = await asyncio.wait_for(self.reader.readline(), self.timeout)
                except Exception as e:
                    pass
                if not data:
                    self.disconnect.emit(self.username, self.addr[0])
                    break
                self.message = data.decode().replace("\r\n","").split(' ')
                print("Received {} from {}".format(self.message, self.addr))
                if not data:
                    print("break")
                    break
                if self.message[0] not in self.command_list.keys():
                    self.respond("500"," Command \"%s\" not understood." % self.message[0])
                else:
                    # command_list.get(self.message[0])()
                    if self.message[0] == "USER":
                        self.user()
                    if self.message[0] == "PASS":
                        self.password()
                    if self.message[0] == "PWD":
                        self.pwd()
                    if self.message[0] == "TYPE":
                        self.type()
                    if self.message[0] == "PASV":
                        await self.pasv()
                    if self.message[0] == "LIST":
                        with await self.cond:
                            self.cond.notify_all()                    

                    if self.message[0] == "CWD":
                        self.cwd()

                    if self.message[0] == "RETR":
                        with await self.cond:
                            self.cond.notify_all() 

                    if self.message[0] == "STOR":
                        with await self.cond:
                            self.cond.notify_all() 
                    if self.message[0] == "MKD":
                        self.mkd()
                    if self.message[0] == "QUIT":
                        self.writer.close()
                        self.disconnect.emit(self.username,self.addr[0])
                        break
                await self.writer.drain()
            print("Close the client socket")
            self.writer.close()
            self.disconnect.emit(self.username,self.addr[0])
        else:
            self.writer.close()
            self.disconnect.emit(self.username, self.addr[0])
        print(self.con)
        self.con = self.con - 1

    def check(self):
        if self.message[0] in ["LIST","RETR","STOR"]:
            return True
        else:
            return False

    async def dtp_handler(self, reader, writer):
        self.respond("150", "File status okay. About to open data connection.")
        print("waiting....")
        with await self.cond:
            await self.cond.wait_for(self.check)
        print("waited")
        if self.message[0] == "LIST":
            await self.list_handler(reader, writer)
        elif self.message[0] == "STOR":
            if self.message[1].startswith('/'):
                self.stor_file = self.rootpath + self.message[1]
            await self.stor_handler(reader, writer)
            self.data_ports.put_nowait(self.available_port)
            self.available_port = None
        elif self.message[0] == "RETR":
            if self.message[1].startswith('/'):
                self.retr_file = self.rootpath + self.message[1]
            await self.retr_handler(reader, writer)
            self.data_ports.put_nowait(self.available_port)
            self.available_port = None
        else:
            print("error")

    async def list_handler(self, reader, writer):
        # self.respond("150" ,"File status okay. About to open data connection.")
        data=""
        # if self.path == '/':
        #     self.path = os.getcwd()
        path = os.listdir(self.path)
        print(self.path)
        for p in path:
            if os.path.isdir(os.path.join(self.path, p)):
                data = data + "drwxr-xr-x 1 owner group           1 Aug 26 16:31 " +  p + "\r\n"
            else:
                size=os.path.getsize(os.path.join(self.path, p))
                data = data + "-rw-r--r-- 1 owner group           {} Aug 26 16:31 ".format(size) + p + "\r\n"
        print(data)
        writer.write(data.encode())
        await self.writer.drain()
        writer.close()
        data = "226 Transfer complete.\r\n"
        print(data)
        self.writer.write(data.encode())
        self.passive_server.close()
        self.data_ports.put_nowait(self.available_port)
        self.available_port = None

    async def retr_handler(self, reader, writer):
        # self.respond("150" ,"File status okay. About to open data connection.")
        file = self.retr_file
        size = os.path.getsize(file)
        print(size)
        self.download.emit(str(size))
        with open(file, 'rb') as f:
            data = f.readlines()
        data = b'\r\n'.join(data)
        print(data)
        writer.write(data)
        await writer.drain()
        writer.close()
        self.passive_server.close()
        self.respond("226","Transfer complete.")

    async def stor_handler(self, reader, writer):
        # self.respond("150" ,"File status okay. About to open data connection.")
        if self.stor_file.startswith('/'):
            file = os.getcwd() + self.stor_file
        else:
            file = self.stor_file
        data = await reader.read()
        size = len(data)
        print("size:{}".format(size))
        self.upload.emit(str(size))
        print(data)
        with open(file, 'wb') as f:
            f.write(data)
        self.passive_server.close()
        self.respond("226","Transfer complete.")

    def respond(self, code, info):
        data = code + ' ' + info + "\r\n"
        print(data)
        self.writer.write(data.encode())
                           
    def user(self):
        if self.message[1] == "anonymous" :
            self.respond("230", "Login successful")
            self.username = "anonymous"
        elif self.user_check(self.message[1]):
            self.respond("331", "User name okay, need password.")
            self.username = self.message[1]
        else:
            self.respond("530", "Not logged in.")
            self.username = None
        if self.username is not None:
            self.onconnect.emit(self.username,self.addr[0]) 

    def user_check(self, user):
        if user == "anonymous":
            return True
        for i in self.username_info:
            if user == i['Name']:
                return True
        return False
            
    def password(self):
        if self.username == None:
            self.respond("332", "Need account for login.")
        for i in self.username_info:
            if self.username == i['Name'] and self.message[1] == i['Password']:
                if os.path.exists(i['SharedFolder']):
                    self.rootpath = i['SharedFolder']
                    self.path = i['SharedFolder']
                else:
                    os.makedirs(i['SharedFolder'])
                    self.rootpath = os.path.abspath(i['SharedFolder'])
                    self.path = self.rootpath                   
                self.respond("230", "Login successful")
                break
        else:
            self.respond("331","Password wrong")
    async def list(self):
        if len(self.message) > 1:
            self.path = self.message[1]
        if self.available_port is not None:
            self.passive_server = await asyncio.start_server(self.list_handler, host=self.host[0], port=self.available_port, loop=self.loop)
        self.data_ports.put_nowait(self.available_port)
        self.available_port = None

    def pwd(self):
        self.respond("250" ,"\"{}\" is the current directory.".format(self.path))

    def cwd(self):
        if self.message[1] != "/":
            if self.message[1] == '..':
                path = os.path.split(self.path)
                self.path = path[0]
            else:
                if self.message[1].startswith('/'):
                    self.path = self.rootpath + self.message[1]
                else:
                    self.path = self.message[1]
        else:
            for i in self.username_info:
                if self.username == i['Name']:
                    self.path = i['SharedFolder']
                    break
            else:
                self.path = '/'
        print(self.path)
        self.pwd()

    def mkd(self):
        if not os.path.exists(self.message[1]):
            if self.message[1].startswith('/'):
                dirpath = self.rootpath + self.message[1]
            else:
                dirpath = self.message[1]
            os.makedirs(dirpath)
            self.respond("257" , "\"{}\" directory created.".format(self.message[1]))

    def type(self):
        if self.message[1] == "A":
            t = "ASCII"
        else:
            t = "Binary"
        self.respond("200","Type set to: {}.".format(t))

    async def retr(self):
        self.retr_file = self.message[1]
        if self.available_port is not None:
            self.passive_server = await asyncio.start_server(self.retr_handler, host=self.host[0], port=self.available_port, loop=self.loop)
        
        self.data_ports.put_nowait(self.available_port)
        self.available_port = None

    async def pasv(self):
        print(self.host)
        host = self.host[0].split('.')
        self.available_port = await self.data_ports.get()
        addr = "({},{},{},{},{},{})".format(*host,int(self.available_port)// 2**8,self.available_port % (2**8))
        self.respond("227" ,"Entering passive mode {}.".format(addr))
        if self.available_port is not None:
            self.passive_server = await asyncio.start_server(self.dtp_handler, host=self.host[0], port=self.available_port, loop=self.loop)

    async def stor(self):
        self.stor_file = self.message[1]
        if self.available_port is not None:
            self.passive_server = await asyncio.start_server(self.stor_handler, host=self.host[0], port=self.available_port, loop=self.loop)
        # self.respond("226","Transfer complete.")
        self.data_ports.put_nowait(self.available_port)
        self.available_port = None

    def ip_handle(self, ip):
        if self.whitelist != []:
            if ip not in self.whitelist:
                return False
        else:
            if ip in self.blacklist:
                return False
        return True

    @pyqtSlot()
    def start(self):
        coro = asyncio.start_server(self.handle_echo, self.host, self.port, loop=self.loop)
        self.server = self.loop.run_until_complete(coro)

        # Serve requests until Ctrl+C is pressed
        print('Serving on {}'.format(self.server.sockets[0].getsockname()))
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.close()

        # Close the server
    @pyqtSlot()
    def close(self):
        self.stop.emit()
        self.server.close()
        # self.loop.run_until_complete(self.server.wait_closed())
        # self.loop.close()

if __name__ == '__main__':
    server = FTPServer(host="0.0.0.0",port=21)
    try:
        server.start()
    except KeyboardInterrupt:
        server.close()