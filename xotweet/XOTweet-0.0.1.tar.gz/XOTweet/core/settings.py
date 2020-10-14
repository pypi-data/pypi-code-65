AUTHORIZATION_TOKEN = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHj" \
                      "hLTvJu4FA33AGWWjCpTnA"

GUEST_TOKEN_URL = "https://api.twitter.com/1.1/guest/activate.json"

SEARCH_URL = "https://api.twitter.com/2/search/adaptive.json?q={}&query_source=typed_query"

LOGGING_CONFIG = {
    'disable_existing_loggers': False,
    'version': 1,
    'formatters': {
        'short': {
            'format': '%(asctime)s %(levelname)s %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'formatter': 'short',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'plugins': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        }
    },
}
