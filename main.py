#!/usr/bin/python

import sys
import loan
import loanGUI

def main(argv):
	l = loan.model.loadAll()
	lApp = loanGUI.application(l, loan.model.fields)


if __name__ == "__main__":
	main(sys.argv[1:])
