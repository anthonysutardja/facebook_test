import random

from facebook_test import util

class FacebookUser(object):
	"""An object to represent a facebook test user. This object doesn't
	provide everything that's available about the user by design. This
	object will aggressively make api request instead of storing internal
	state to ensure it always gives you the correct information about a
	user
	"""

	def __init__(self, parent_app, fbuid, login_url):
		"""Create an instance of the facebook user

		Args:
			parent_app - The app the user was created for
			fbuid - The facebook user id
			login_url - A url that can be used to log in a
				user in a browser
		"""
		self.__parent_app = parent_app
		self.fbuid = fbuid
		self.login_url = login_url

	def create_friendship(self, other_fbuid):
		raise NotImplementedError

	def delete(self):
		return util.graph_get(self.url_path, {
			'method': 'delete',
			'access_token': self.__parent_app.app_access_token
		})

	def login(self):
		raise NotImplementedError

	@property
	def email(self):
		"""The email of the user. Note this request will
		fail if the parent app doesn't have email permissions
		on the user account
		"""
		return util.json.loads(util.graph_get(self.url_path, {
			'access_token': self.__parent_app.app_access_token
		}))['email']

	@property
	def url_path(self):
		return '/{fbuid}'.format(fbuid=self.fbuid)

	def generate_shortlived_password(self):
		"""Creates a new password for the user.

		Note: there's not way of accessing the existing password
			of a facebok user. facebook doesn't provide an api
			for this

		Returns:
			The new password or None if a password couldn't be set
		"""
		password = str(random.getrandbits(128))

		success = util.graph_get(self.url_path, {
			'method': 'post',
			'password': password,
			'access_token': self.__parent_app.app_access_token
		})

		return password if success else None

	@classmethod
	def from_facebook_user_dict(cls, parent_app, user_dict):
		"""Factory method for creating a FacebookUser instance
		for a graph api response
		"""
		return cls(
			parent_app,
			user_dict['id'],
			user_dict['login_url'],
		)

	def __repr__(self):
		return '<FacebookUser: {fbuid}>'.format(fbuid=self.fbuid)
