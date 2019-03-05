import datetime
import logging
log = logging.getLogger(__name__)


valid_formats = ['%Y', "%Y-%M-%D", "%Y%M%D",
                 "%d %b %Y", "%d %b %Y %H:%M:%S", "%b %Y %H:%M:%S"]


def get_date_dictionary(key: str, date: str):
    """
    format dictionary to program required structure
    :param key: the key that we are currently processing
    :param date: a date to translate to datetime object
    :return: a field if successful, else error field and raw value
    """
    date_obj = get_date(date)
    if date_obj:
        return {key: date_obj}
    else:
        return {key: {'raw': date, 'error': True}}


def get_date(date: str):
    """
    using the locally defined 'fmt' options, attempt to
    format the date string to a datetime object
    :param date: a date string
    :return: a datetime object
    """
    # deal with exception where it is a year only
    try:
        if len(date) == 4 and int(date) > 1000:
            log.debug("suspected YYYY only date: {}".format(date))
    except ValueError as e:
        pass
    for fmt in valid_formats:
        try:
            return datetime.datetime.strptime(date, fmt)
        except Exception as e:
            pass
    return None
