"""

- add translate.yandex.ru (v)
	https://translate.yandex.ru

- add translate.tatar (v)
	https://translate.tatar

- add translate.google.com
	pip install googletrans

"""

import os
import sys
import json
import string
import re
import requests
import warnings
import threading
import time
from googletrans import Translator

lock_CookieFile = threading.Lock()

user_agent = 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'


class Tools:
	def __init__(self):
		pass

	def json_encode(self, dict_value):
		return json.dumps(dict_value)

	def json_decode(self, json_string):
		return json.loads(json_string)


class State:
	def __init__(self):
		self.state = lock_CookieFile
		cwd = os.path.abspath(os.path.dirname(__file__))
		self.state_file = os.path.abspath(os.path.join(cwd, "cookies.json"))

	def state_update(self, result):
		result = Tools().json_encode(result)

		self.state.acquire()
		with open(self.state_file, "wb") as f:
			f.write(result.encode())
		self.state.release()

	def state_make(self):
		result = dict()
		self.state_update(result)

	def state_read(self):
		if not os.path.exists(self.state_file):
			# make state file
			self.state_make()

		self.state.acquire()
		with open(self.state_file, "rb") as f:
			result = f.read().decode()
		self.state.release()

		result = Tools().json_decode(result)
		return result

	def state_write(self, element, cookie):
		result = self.state_read()

		result[ element ] = cookie

		self.state_update(result)
		return True


def get_sid(get_new=False):
	global user_agent
	result = ''

	try:
		headers = {'User-agent': user_agent,
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
					'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
					'Cache-Control': 'max-age=0',
					'Connection': 'keep-alive'}

		# get sid first
		state = State().state_read()
		if get_new:

			url = 'https://translate.yandex.ru/?lang=ru-tt'
			cookies = ''
			if 'cookies' in state:
				cookies = state['cookies']
				print("Cookies:", cookies)

			r = requests.get(url, headers=headers, cookies=cookies, verify=False)

			if r.status_code == requests.codes.ok:
				if 'Content-Type' in r.headers:
					if 'text' in r.headers['Content-Type'] or 'html' in r.headers['Content-Type']:

						# update cookies
						cookies = r.cookies.get_dict()
						if len(cookies) > 0:
							State().state_write('cookies', cookies)

						answer = r.content.decode('utf-8')

						# SID: '91b0b84d.6edfe0c5.2a935cbc',
						answer = re.findall(r'SID\: \'([a-zA-Z0-9_.]+)\'\,', answer, re.M)
						if len(answer) > 0:
							
							answer = answer[0].split(".")
							for i in range(0, len(answer)):
								answer[i] = answer[i][::-1]
							result = ".".join(answer) + "-0-0"

							if len(result) > 0:
								State().state_write('sid', result)
								print("SID:", result)
		else:
			if 'sid' in state:
				result = state['sid']

	except BaseException as e:
		print(str(e))

	return result


# WARNING (!!!)
# Enter in Windows console 'chcp 65001' to support UTF-8
# set PATH=%PATH%D:\folder\
#------------------------------------------------------
#  translate_yandex function
#------------------------------------------------------
def translate_yandex(text):
	global user_agent
	result = ''

	try:
		headers = {'User-agent': user_agent,
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
					'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
					'Cache-Control': 'max-age=0',
					'Connection': 'keep-alive',
					'Referer': 'https://yandex.ru/'}

		url = 'https://translate.yandex.net/api/v1/tr.json/translate?id={:s}&srv=tr-text&lang=ru-tt&reason=paste'.format(get_sid())  # cut, paste, auto

		# get cookies first
		state = State().state_read()

		cookies = ''
		if 'cookies' in state:
			cookies = state['cookies']

		r = requests.post(url, headers=headers, cookies=cookies, data = {'text': text, 'options': 4}, verify=False)
		#print(r.headers, r.content);exit()

		if r.status_code == requests.codes.ok:
			if 'Content-Type' in r.headers:
				if 'json' in r.headers['Content-Type']:

					# r.json
					answer = json.loads(r.content.decode('utf-8'))

					if 'text' in answer and 'code' in answer:

						if answer['code'] == 200:
							result = answer['text'][0]
						else:
							print("translate_yandex error translate, updating sid")
							if 'message' in answer:
								print(answer['message'])

							time.sleep(2)
							get_sid(True)

				else:
					print("translate_yandex error wrong content-type: {:s}".format(r.headers['Content-Type']))

			else:
				print("translate_yandex error wrong headers: {:s}".format(r.headers))

		else:
			print("translate_yandex error wrong status: {:d}, updating sid".format(int(r.status_code)))

			time.sleep(2)
			get_sid(True)

	except BaseException as e:
		print(str(e))

	return result


#------------------------------------------------------
#  translate_tatar function
#------------------------------------------------------
def translate_tatar(text):
	global user_agent
	result = ''

	try:
		headers = {'User-agent': user_agent,
					'Accept': '*/*',
					'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
					'Cache-Control': 'max-age=0',
					'Connection': 'keep-alive',
					'Host': 'translate.tatar',
					'Referer': 'https://translate.tatar/'}

		url = 'https://translate.tatar/translate?lang=0&text={:s}'.format(text)

		# cookies (?)
		cookies = dict()

		r = requests.get(url, headers=headers, cookies=cookies, verify=False)
		# print(r.headers, r.content);exit()

		if r.status_code == requests.codes.ok:
			if 'Content-Type' in r.headers:
				if 'text' in r.headers['Content-Type'] or 'xml' in r.headers['Content-Type']:
					answer = r.content.decode('utf-8')

					if len(answer) > 0:
						# parse XML
						result = answer

				else:
					print("translate_tatar error wrong content-type: {:s}".format(r.headers['Content-Type']))

			else:
				print("translate_tatar error wrong headers: {:s}".format(r.headers))

		else:
			print("translate_tatar error wrong status: {:d}".format(int(r.status_code)))
			time.sleep(2)

	except BaseException as e:
		print(str(e))

	return result


#------------------------------------------------------
#  translate_google function
#------------------------------------------------------
def translate_google(text):
	translator = Translator()

	result = translator.translate(text, src='ru', dest='tt')

	return result


if __name__ == "__main__":
	# requests lib warns about verify=False
	if not sys.warnoptions:
		warnings.simplefilter("ignore")

	# get_sid(True)

	time.sleep(2)
	print(translate_yandex('привет мой друг'))
	# print(translate_tatar('привет мой друг'))

	# doesnt work
	# print(translate_google('привет мой друг'))
