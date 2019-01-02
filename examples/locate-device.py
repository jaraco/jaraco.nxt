from jaraco.nxt import locator
import logging


def run():
	logging.basicConfig(level=logging.DEBUG)
	locator.find_brick()


__name__ == '__main__' and run()
