import logging
import os

import datetime
from tornado import gen
from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.ioloop import IOLoop
import tornado.web


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


client = AsyncHTTPClient()


class HttpProxyHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        logger.info("Processing url %s", self.request.uri)

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

            request = HTTPRequest(url=self.request.uri, headers=headers)

            response = yield gen.Task(client.fetch, request)

            logger.info("Target response status %s", response.code)

            for header_name, header_value in response.headers.get_all():
                logger.debug("Adding response header %s=%s", header_name, header_value)
                self.add_header(header_name, header_value)

            if response.body:
                content_length = len(response.body)
                self.set_header("Content-Length", content_length)
                self.write(response.body)

                self.application.bytes_transferred += content_length

            self.finish()


class StatsHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        self.write({
            "bytes_transferred": self.application.bytes_transferred,
            "uptime_seconds": (datetime.datetime.now() - self.application.start_time).seconds,
        })
        self.finish()


class FancyStatsHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        self.render(
            "templates/stats.html",
            uptime_seconds=(datetime.datetime.now() - self.application.start_time).seconds,
            bytes_transferred=self.application.bytes_transferred
        )


class AsyncProxy(tornado.web.Application):
    def __init__(self):
        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
        }

        handlers = [
            (r"/stats", StatsHandler),
            (r"/fancystats", FancyStatsHandler),
            (r"/static/.*", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
            (r".*", HttpProxyHandler),
        ]

        self.bytes_transferred = 0
        self.start_time = datetime.datetime.now()

        super().__init__(handlers, **settings)


if __name__ == "__main__":
    port = os.getenv("ASYNC_PROXY_PORT", 8000)
    address = os.getenv("ASYNC_PROXY_ADDRESS", "0.0.0.0")

    app = AsyncProxy()
    app.listen(port, address=address)

    IOLoop.instance().start()
