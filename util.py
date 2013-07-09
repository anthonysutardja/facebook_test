import functools
import simplejson as json
import urllib
import urllib2

#pyflakes
json = json

def enum(**enums):
	return type('Enum', (), enums)

PERMISSION = enum(
	EMAIL=0x01,
	READ_STREAM=0x02,
	BIRTHDAY=0x04,
	LOCATION=0x06
)

_PERMISSION_TO_API_REQUEST = {
	PERMISSION.EMAIL: 'email',
	PERMISSION.READ_STREAM: 'read_stream',
	PERMISSION.BIRTHDAY: 'user_birthday',
	PERMISSION.LOCATION: 'user_location'
}

def get(path, param_dict, domain):
	""" Perform a https get request in a sane way

	Args:
		path - The path of the url
		param_dict - a dict mapping query arguments to values
		domain - The domain of the url
	"""
	params = urllib.urlencode(param_dict)

	req = urllib2.Request(
		'https://{domain}{path}?{query}'.format(domain=domain, path=path, query=params)
	)

	response = urllib2.urlopen(req)
	return response.read()

graph_get = functools.partial(get, domain='graph.facebook.com')
