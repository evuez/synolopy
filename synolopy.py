import logging
import json
from urllib import error
from urllib.request import Request
from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.parse import urlunparse
from urllib.parse import urljoin
from urllib.parse import parse_qs
from urllib.parse import urlencode


logging.basicConfig(level=logging.DEBUG)


class RequestError(Exception):
	pass


class API(object):
	NAME = None
	VERSION = None
	BASE = None
	METHODS = None
	AUTH_HANDLER = None

	def __init__(self, root, credentials):
		assert len(credentials) == 2

		self.root = root
		self._sid = None
		self._credentials = credentials

	def url_for(self, data=None):
		"""
		data will override default query string if any
		"""
		url = urljoin(self.root, self.BASE)
		if data:
			url = list(urlparse(url))
			url[4] = data
			url = urlunparse(url)
		return url

	def req_for(self, name, **data):
		_data = {
			'api': self.NAME,
			'version': self.VERSION,
			'session': self.__class__.__name__,
			'format': 'sid',
			'method': name
		}

		if self._sid:
			_data['_sid'] = self._sid
		else:
			_data['account'] = self._credentials[0]
			_data['passwd'] = self._credentials[1]

		data = urlencode(dict(list(_data.items()) + list(data.items())))
		method = self.METHODS[name]

		return Request(
			self.url_for(data if method == 'GET' else None),
			data=data.encode('utf-8') if method == 'POST' else None
		)

	def request(self, name, **kwargs):
		return urlopen(self.req_for(name, **kwargs))

	def __getattr__(self, name):
		if name not in self.METHODS:
			raise AttributeError
		def method(**kwargs):
			try:
				res = json.loads(self.request(
					name, **kwargs
				).read().decode('utf-8'))
				if 'error' in res:
					raise RequestError('errno: ', res['error']['code'])
				return res.get('data', None)
			except  (error.URLError, TypeError, RequestError) as e:
				logging.error("An error occurred in %s: %s", name, e)
		return method

	def login(self):
		self._sid = self.AUTH_HANDLER(
			self.root,
			self._credentials
		).build_sid()

	def logout(self):
		self.AUTH_HANDLER(self.root, self._credentials).reset_sid()
		self._sid = None


class Auth(API):
	NAME = 'SYNO.API.Auth'
	VERSION = 2
	BASE = 'auth.cgi'
	METHODS = {
		'login': 'GET',
		'logout': 'GET',
	}

	def build_sid(self):
		return self.__getattr__('login')()['sid']

	def reset_sid(self):
		self.__getattr__('logout')()


class DownloadStationTask(API):
	NAME = 'SYNO.DownloadStation.Task'
	VERSION = 1
	BASE = 'DownloadStation/task.cgi'
	METHODS = {
		'create': 'POST',
	}
	AUTH_HANDLER = Auth
