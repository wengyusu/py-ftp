# import asyncio
# import aioftp

# users = (aioftp.User("test",
#     "test",
#     home_path="/d/",
#     permissions=(
#     aioftp.Permission("/d/", readable=True, writable=True),
#         )          
#     )
# )

# loop = asyncio.get_event_loop()
# server = aioftp.Server()
# loop.run_until_complete(server.start('0.0.0.0', 21))
# try:
#     loop.run_forever()
# except KeyboardInterrupt:
#     loop.run_until_complete(server.close())
#     loop.close()

import os

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

class FTP:
    def __init__(self, host="127.0.0.1", port=21, blacklist=[], whitelist=[]):
        self.host = host
        self.port = port
        self.blacklist = blacklist
        self.whitelist = whitelist
        # Instantiate a dummy authorizer for managing 'virtual' users
        authorizer = DummyAuthorizer()

        # Define a new user having full r/w permissions and a read-only
        # anonymous user
        authorizer.add_user('user', '12345', '.', perm='elradfmwMT')
        authorizer.add_anonymous(os.getcwd())

        # Instantiate FTP handler class
        handler = FTPHandler
        handler.authorizer = authorizer

        # Define a customized banner (string returned when client connects)
        handler.banner = "pyftpdlib based ftpd ready."

        # Specify a masquerade address and the range of ports to use for
        # passive connections.  Decomment in case you're behind a NAT.
        #handler.masquerade_address = '151.25.42.11'
        #handler.passive_ports = range(60000, 65535)

        # Instantiate FTP server class and listen on 0.0.0.0:2121
        
        address = (self.host, self.port)
        self.server = FTPServer(address, handler)

        # set a limit for connections
        self.server.max_cons = 256
        self.server.max_cons_per_ip = 5

    # add blacklist
        self.server.blacklist = self.blacklist
        self.server.whitelist = self.whitelist

    # start ftp server
    def start(self):
        self.server.serve_forever()

    def close(self):
        self.server.close()

if __name__ == '__main__':
    ftpserver = FTP()
    ftpserver.start()