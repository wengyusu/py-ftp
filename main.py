import asyncio
import aioftp


loop = asyncio.get_event_loop()
server = aioftp.Server()
loop.run_until_complete(server.start('127.0.0.1', 7777))
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(server.close())
    loop.close()