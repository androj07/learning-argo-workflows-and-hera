import json
import logging
import sys


def get_module_logger(mod_name):
    """
    To use this, do logger = get_module_logger(__name__)
    """
    _logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    _logger.setLevel(logging.DEBUG)
    return _logger


if __name__ == '__main__':
    logger = get_module_logger('main')
    logger.info(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        logger.info(f"Argument {i:>6}: {arg}")

    if sys.argv[1] == "--generator":

        for i in range(int(sys.argv[2])):
            json.dump({"value": i}, sys.stdout)
