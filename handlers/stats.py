import logging

logger = logging.getLogger()


def handler(func):
    def wrapper(update, context):
        msg = update.message.text
        user = update.effective_user
        username = user.username
        uid = user.id
        logger.info('username: {}, id: {}, msg: {}'.format(username, uid, msg))
        func(update, context)
    return wrapper
