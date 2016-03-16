# Copyright (C) TEONITE - http://teonite.com
import logging
import os

import datetime
from tornado import gen
from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.ioloop import IOLoop
import tornado.web


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


class HttpProxyHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.client = AsyncHTTPClient()

    @gen.coroutine
    def get(self):
        logger.info("New request from %s - url %s", self.request.remote_ip, self.request.uri)

        range_param = self.get_argument("range", None)
        range_header = self.request.headers.get("Range", None)

        if range_param and range_header and range_param != range_header:
            logger.error("Inconsistent range header %s and param %s", range_header, range_param)
            self.send_error(416)
        else:
            headers = self.request.headers

            if range_param:
                logger.info("Setting Range header based on range query parameter")
                headers["Range"] = range_param

            logger.debug("Setting target request headers %s", list(headers.get_all()))

            request = HTTPRequest(url=self.request.uri, headers=headers, streaming_callback=self._streaming_callback)

            response = yield gen.Task(self.client.fetch, request)

            logger.info("Target response status %s", response.code)

            for header_name, header_value in response.headers.get_all():
                logger.debug("Adding response header %s=%s", header_name, header_value)
                self.add_header(header_name, header_value)

            self.finish()

    def _streaming_callback(self, chunk):
        chunk_length = len(chunk)
        logger.debug("Writing chunk of %s bytes", chunk_length)
        self.write(chunk)
        self.flush()
        self.application.bytes_transferred += chunk_length


class StatsHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        self.render(
            "templates/stats.html",
            uptime_seconds=self.application.uptime_seconds,
            bytes_transferred=self.application.bytes_transferred
        )


class AsyncProxy(tornado.web.Application):
    def __init__(self):
        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
        }

        handlers = [
            (r"/stats", StatsHandler),
            (r"/static/.*", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
            (r".*", HttpProxyHandler),
        ]

        self.bytes_transferred = 0
        self.start_time = datetime.datetime.now()

        super().__init__(handlers, **settings)

    @property
    def uptime_seconds(self):
        return (datetime.datetime.now() - self.start_time).seconds


if __name__ == "__main__":
    port = os.getenv("ASYNC_PROXY_PORT", 8000)
    address = os.getenv("ASYNC_PROXY_ADDRESS", "0.0.0.0")

    app = AsyncProxy()
    app.listen(port, address=address)

    logger.info("Copyright (C) TEONITE - http://teonite.com")
    logger.info("Proxy listening on %s:%s", address, port)

    IOLoop.instance().start()
