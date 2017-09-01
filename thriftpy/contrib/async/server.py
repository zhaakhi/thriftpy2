# -*- coding: utf-8 -*-
import asyncio
from thriftpy.server import TServer, logger
from thriftpy.transport import TTransportException


class TAsyncServer(TServer):

    def __init__(self, *args, **kwargs):
        TServer.__init__(
            self,
            *args,
            **kwargs
        )
        self.closed = False

    def serve(self):
        self.trans.listen()
        loop = asyncio.get_event_loop()
        self.server = loop.run_until_complete(self.trans.accept(self.handle))
        try:
            loop.run_forever()
        except:
            self.close()
            raise

    @asyncio.coroutine
    def handle(self, client):
        itrans = self.itrans_factory.get_transport(client)
        otrans = self.otrans_factory.get_transport(client)
        iprot = self.iprot_factory.get_protocol(itrans)
        oprot = self.oprot_factory.get_protocol(otrans)
        try:
            while not client.reader.at_eof():
                yield from self.processor.process(iprot, oprot)
        except TTransportException:
            pass
        except Exception as x:
            logger.exception(x)

        itrans.close()
        otrans.close()

    @asyncio.coroutine
    def close(self):
        self.server.close()
        yield from self.server.wait_closed()
        self.closed = True
