import logging
import build


def init(log_file=None, log_level=logging.INFO):
    """
    get a logger that prints to a log_file, and to stdout/terminal. Is root logger so returns nothing
    :param log_file:
    :param log level for logger
    """
    if not log_file:
        log_file = build.__name__ + '.log'

    # we don't require finely grained contextual info, so using straight string modifier instead of filters
    formatter = logging.Formatter(
        '%(asctime)s [{}] %(levelname)s %(module)s - %(funcName)s: %(message)s'.format(build.__version__))
    log = logging.getLogger()
    log.setLevel(log_level)

    if len(log.handlers) > 0:
        log.handlers = []

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)
    return log
