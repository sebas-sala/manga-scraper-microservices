import logging.config
import colorlog

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        },
          'colored': {
            '()': colorlog.ColoredFormatter,
            'format': '[%(asctime)s] %(log_color)s%(levelname)s%(reset)s in %(module)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',  
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
        },
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'pika': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        }
    },
})
