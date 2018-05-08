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
 
blacklist = []
whitelist = []
def main():
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
    address = ('0.0.0.0', 21)
    server = FTPServer(address, handler)

    # set a limit for connections
    server.max_cons = 256
    server.max_cons_per_ip = 5

    server.blacklist=['127.0.0.1']

    # start ftp server
    server.serve_forever()

if __name__ == '__main__':
    main()