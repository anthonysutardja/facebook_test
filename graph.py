# -*- coding: utf-8 -*-
import urlparse

from facebook_test import util
from facebook_test.user import FacebookUser

#TODO: These exceptions need to be hooked up.
class TestUserCantDelete(Exception):
	"""Test user is associated with multiple apps"""
	pass

class TestUserCantRemoveApp(Exception):
	"""Test user must be associated with at least one app"""
	pass

class TestUserAccountInvalidId(Exception):
	"""Test user is not associated with this app"""
	pass

class UnknownFacebookError(Exception):
	"""Facebook did something weird/unexpected"""
	pass

class TooManyTestAccountsCreated(Exception):
	"""The app has created more than the 2000 test accounts"""
	pass

class App(object):
	"""An object for interacting with the user test interface for a facebook app"""

	def __init__(self, app_id, app_secret, open_graph_test_user_fbuid):
		"""Creates a connection to a facebook graph application

		Args:
			app_id - The facebook app id
			app_secret - The facebook app secret
			open_graph_test_user_fbuid - The reserved facebook user id that
				cannot be removed/modified in the app. This user is
				automatically created by facebook when you make a graph
				application, for the purposes of this library, we completely
				ignore the existence of this user)
		"""
		self.app_id = app_id
		self.__app_secret = app_secret
		self.__app_access_token = None
		self.__open_graph_test_user_fbuid = open_graph_test_user_fbuid

	def create_user(self, first_name, last_name, permissions, locale='en_US', installed=True):
		"""Create a test user associated with the app

		Args:
			first_name - The first name of the user
			last_name - The last name of the user
			permissions - The permissions being requested for the user (see facebook_test.util)
				for permission options
			locale - The locale of the user account
			installed - A flag to indicated whether or not you want the user to be connect to
				the app

		Returns:
			A FacebookUser instance
		"""
		user_dict = util.json.loads(util.graph_get(
			'/{app_id}/accounts/test-users'.format(app_id=self.app_id), {
				'installed': installed,
				'name': first_name + ' ' + last_name,
				'locale': locale,
				'permissions': ','.join([v for k, v in util._PERMISSION_TO_API_REQUEST.iteritems() if k & permissions]),
				'method': 'post',
				'access_token': self.app_access_token,
				'redirect_uri': ''
			}
		))

		return FacebookUser.from_facebook_user_dict(self, user_dict)

	def get_all_users(self, after=None):
		"""Generates all available users of the app

		Args:
			after - Used for pagination

		Generates:
			FacebookUser instances
		"""
		params =  {
			'access_token': self.app_access_token
		}

		if after:
			params['after'] = after

		response = util.json.loads(
			util.graph_get('/{app_id}/accounts/test-users'.format(app_id=self.app_id), params)
		)

		if len(response['data']) == 0:
			return

		for partial_user_dict in response['data']:
			other_partial_user_dict = self.__get_user(partial_user_dict['id'])
			other_partial_user_dict.update(partial_user_dict)

			user = FacebookUser.from_facebook_user_dict(
				self,
				other_partial_user_dict
			)

			if user.fbuid != str(self.__open_graph_test_user_fbuid):
				yield user

		for user in self.get_all_users(after=response['paging']['cursors']['after']):
			yield user

	@property
	def app_access_token(self):
		""" The application access token of the app"""

		if self.__app_access_token is None:
			query_string = util.graph_get(
				'/oauth/access_token', {
					'client_id': self.app_id,
					'client_secret': self.__app_secret,
					'grant_type': 'client_credentials',
				}
			)

			query = urlparse.parse_qs(query_string, strict_parsing=True)

			access_token = query.get('access_token', None)

			if access_token is None or len(access_token) != 1:
				# Go home facebook, you're drunk.
				raise UnknownFacebookError

			self.__app_access_token = access_token[0]

		return self.__app_access_token

	def __get_user(self, fbuid):
		return util.json.loads(util.graph_get(
			'/{fbuid}'.format(fbuid=fbuid), {
				'access_token': self.app_access_token
			}
		))
