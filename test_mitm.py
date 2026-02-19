from mitmproxy.tools.dump import DumpMaster
from mitmproxy import options
import asyncio

async def main():
    print("Import successful")
    opts = options.Options(listen_host="127.0.0.1", listen_port=8081)
    print("Options created")
    m = DumpMaster(opts)
    print("DumpMaster created")
    # await m.run() # Don't run to avoid blocking

if __name__ == "__main__":
    asyncio.run(main())
