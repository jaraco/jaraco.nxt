import logging

from jaraco.nxt import locator


def run():
    logging.basicConfig(level=logging.DEBUG)
    locator.find_brick()


__name__ == '__main__' and run()
