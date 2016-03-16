# Copyright (C) TEONITE - http://teonite.com
import time

from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.httpclient import HTTPError
from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase, gen_test

from asyncproxy.asyncproxy import AsyncProxy


class AsyncProxyTestCase(AsyncHTTPTestCase):

    def setUp(self):
        self.url = "http://cdn3.sbnation.com/assets/3786371/DOGE-12.jpg"
        super().setUp()

    def get_app(self):
        return AsyncProxy()

    def get_new_ioloop(self):
        return IOLoop.instance()

    def get_http_client(self):
        return CurlAsyncHTTPClient(io_loop=self.io_loop)

    @gen_test
    def test_proxy_without_range(self):
        response = yield self.http_client.fetch(self.url, proxy_host="localhost", proxy_port=self.get_http_port())
        self.assertEqual(response.code, 200)
        self.assertEqual(int(response.headers["Content-Length"]), 84378)

    @gen_test
    def test_proxy_with_range_header(self):
        headers = {
            "Range": "bytes=0-99"
        }
        response = yield self.http_client.fetch(self.url, headers=headers, proxy_host="localhost",
                                                proxy_port=self.get_http_port())
        self.assertEqual(response.code, 200)
        self.assertEqual(int(response.headers["Content-Length"]), 100)

    @gen_test
    def test_proxy_with_range_param(self):
        response = yield self.http_client.fetch("%s?range=bytes=0-99" % self.url, proxy_host="localhost",
                                                proxy_port=self.get_http_port())
        self.assertEqual(response.code, 200)
        self.assertEqual(int(response.headers["Content-Length"]), 100)

    @gen_test
    def test_proxy_range_conflict(self):
        headers = {
            "Range": "bytes=0-199"
        }

        with self.assertRaises(HTTPError):
            yield self.http_client.fetch("%s?range=bytes=0-99" % self.url, headers=headers,
                                         proxy_host="localhost", proxy_port=self.get_http_port())

    def test_stats_uptime(self):
        time.sleep(1)
        self.assertGreater(self._app.uptime_seconds, 0)

    def test_stats_bytes_tranfered(self):
        self.test_proxy_with_range_header()
        self.assertEqual(self._app.bytes_transferred, 100)
