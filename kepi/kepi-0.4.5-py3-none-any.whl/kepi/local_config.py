ALLOWED_HOSTS = [
        'sandy-heath.thurman.org.uk',
        '127.0.0.1',
        ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/var/www/data/kepi.sqlite3',
    }
}

KEPI = {
        'LOCAL_OBJECT_HOSTNAME': 'sandy-heath.thurman.org.uk',

        'TOMBSTONES': True,

        'OBJECT_LINK': '/%(number)s',
        'USER_LINK': '/users/%(username)s',
        'COLLECTION_LINK': '/users/%(username)s/%(listname)s',
        'STATUS_LINK': '/users/%(username)s/%(id)s',
        'STATUS_FEED_LINK': '/users/%(username)s/feed/%(id)s',
        'USER_FEED_LINK': '/users/%(username)s/feed',
        'USER_WEBFINGER_LINK': '/.well-known/webfinger?resource=acct:%(username)s@%(hostname)s',
        'USER_FOLLOWING_LINK': '/users/%(username)s/following',
        'USER_FOLLOWERS_LINK': '/users/%(username)s/followers',
        'USER_INBOX_LINK': '/users/%(username)s/inbox',
        'USER_OUTBOX_LINK': '/users/%(username)s/outbox',
        'USER_FEATURED_LINK': '/users/%(username)s/featured',
        'FOLLOW_REQUEST_LINK' : '/users/%(username)s/follow/%(number)x',
        'SHARED_INBOX_LINK': '/sharedInbox',
        'ACTIVITY_LINK': '/activity/%(serial)s',

        # the "{uri}" in AUTHORIZE_FOLLOW_LINK is for the client to
        # fill in, not us. We pass it out as is.
        'AUTHORIZE_FOLLOW_LINK': '/authorize_follow?acct={uri}',

        'INSTANCE_NAME': 'kepi server',
        'INSTANCE_DESCRIPTION': 'this is a test server',
        'CONTACT_ACCOUNT': 'marnanel',
        'CONTACT_EMAIL': 'marnanel@example.com',
        'LANGUAGES': ['en'],


        }
