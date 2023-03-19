from authlib.integrations.flask_client import OAuth
from oauth_config import APP_SECRET_KEY, GOOGLE_CLIENT_SECRET, GOOGLE_CLIENT_ID


def create_oauth(app):
    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
        # This is only needed if using openId to fetch user info
        client_kwargs={'scope': 'email profile'},
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
    )
    return oauth
