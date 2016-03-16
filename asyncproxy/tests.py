import json

import time

from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase

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

    def test_proxy_without_range(self):
        self.http_client.fetch(self.url, self.stop, proxy_host="localhost", proxy_port=self.get_http_port())
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(int(response.headers["Content-Length"]), 84378)

    def test_proxy_with_range_header(self):
        headers = {
            "Range": "bytes=0-99"
        }
        self.http_client.fetch(self.url, self.stop, headers=headers, proxy_host="localhost",
                               proxy_port=self.get_http_port())
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(int(response.headers["Content-Length"]), 100)

    def test_proxy_with_range_param(self):
        self.http_client.fetch("%s?range=bytes=0-99" % self.url, self.stop, proxy_host="localhost",
                               proxy_port=self.get_http_port())
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(int(response.headers["Content-Length"]), 100)

    def test_proxy_range_conflict(self):
        headers = {
            "Range": "bytes=0-199"
        }
        self.http_client.fetch("%s?range=bytes=0-99" % self.url, self.stop, headers=headers, proxy_host="localhost",
                               proxy_port=self.get_http_port())
        response = self.wait()
        self.assertEqual(response.code, 416)

    def test_stats_uptime(self):
        time.sleep(1)
        self.assertGreater(self._app.uptime_seconds, 0)

    def test_stats_bytes_tranfered(self):
        self.test_proxy_with_range_header()
        self.assertEqual(self._app.bytes_transferred, 100)
