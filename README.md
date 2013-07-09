facebook_test
=============

A python wrapper around the facebook graph test user api. This is super useful if you're writing selenium
tests that need to interact with the facebook api.

Example usage:

```python
from facebook_test.graph import App
from facebook_test.util import PERMISSION

app = App(app_id, app_secret, open_graph_test_user_fbuid=reserved_open_graph_fbuid)

user = app.create_user(
  'Ken', 
  'Struys', 
  permissions=PERMISSION.READ_STREAM | PERMISSION.EMAIL
)

user.login_url # Can be used to log yourself in a the test user (make a get request in your browser)

user.email # Retrieves the email address associated with the user

user.create_friendshop(other_fbuid) # Makes the user friends with another user on facebook

user.delete() # Deletes the user account
```

See https://developers.facebook.com/docs/test_users/ for explanation of underlying facebook api
