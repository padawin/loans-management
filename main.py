#!/usr/bin/python

"""
Entry point of the application
"""

import sys
import loan
import loanGUI


def main(argv):
	"""
	Main method. Here are loaded the existing loans, and then the GUI is
	created.
	"""
	l = loan.model.loadAll()
	lApp = loanGUI.application(l, loan.model.fields)
	sys.exit(lApp.run())


if __name__ == "__main__":
	main(sys.argv[1:])
