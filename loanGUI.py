# -*- coding: utf8 -*-

from PyQt4 import QtCore
from PyQt4 import QtGui
import sys
import config
import operator
import csv

class application(QtGui.QApplication):
	def __init__(self, data, headers):
		super(application, self).__init__(sys.argv)
		self.data = data
		self.headers = headers
		self.widget = mainWindow(self)

	def run(self):
		return self.exec_()

class mainWindow(QtGui.QMainWindow):
	def __init__(self, app):
		super(mainWindow, self).__init__()
		self._app = app
		(self._orderCol, self._orderWay) = (0, 1)
		#creation of the UI
		self.initUI()

	#Create the UI
	def initUI(self):
		#top menu
		self.setMenuBar(menu(self))
		self.setStatusBar(QtGui.QStatusBar())
		#creation fo the window
		self._create()
		#definition if window informations (size, position, title)
		self._setWindowInfos()
		#display the Whole Thing
		self.show()

	#method which create the UI
	def _create(self):
		# central widget
		centralWidget = QtGui.QWidget(self)
		# main layout
		vbox = QtGui.QVBoxLayout(centralWidget)
		vbox.setMargin(10)

		vbox.addWidget(table(self, self._app.headers, self._app.data, self._orderCol, self._orderWay))
		newLoanFieldButton = QtGui.QPushButton('Add Loan')
		#button event
		#~ newTicketFieldButton.clicked.connect(self._addLoan)
		vbox.addWidget(newLoanFieldButton)

		self.setCentralWidget(centralWidget)

	def displayMessage(self, text):
		self.statusBar().showMessage(text)

	#define window informations
	def _setWindowInfos(self):
		# default size
		self.setGeometry(300, 300, 600, 600)
		#~ self.setWidth()
		self.setWindowTitle('My loans')

	def _setSortCol(self, col):
		self._orderCol = col

	def _setSortOrder(self, order):
		self._orderWay = order

	def _addNewLoan(self):
		pass

	def _saveLoans(self):
		#get the tab name and index

		fileName = QDir.home().absolutePath() + QDir.separator() + ("loans.csv")
		writer = csv.writer(open(fileName, "wb"))

		csvData = []
		for i in enumerate(self._app.data):
			tmp = []
			for v in i[1].values():
				try:
					tmp.append(v.encode('utf-8'))
				except:
					tmp.append(v)
			csvData.append(tmp)

		writer.writerows(csvData)
		self.displayMessage("Your loans have been saved in the file %s" % (fileName))


class tableModel(QtCore.QAbstractTableModel):
	def __init__(self, data, headerdata, parent=None, *args):
		""" data: a list of lists
			headerdata: a list of strings
		"""
		QtCore.QAbstractTableModel.__init__(self, parent, *args)

		self._parent = parent
		self.arraydata = data
		self.headerdata = headerdata

	def rowCount(self, parent):
		return len(self.arraydata)

	def columnCount(self, parent):
		if len(self.arraydata) > 0:
			return len(self.arraydata[0])
		return 0

	def data(self, index, role):
		if not index.isValid():
			return QtCore.QVariant()
		elif role == QtCore.Qt.ForegroundRole:
			return QtCore.QVariant(QtGui.QColor('#073642'))
		elif role == QtCore.Qt.BackgroundRole:
			return QtCore.QVariant(QtGui.QColor('#fdf6e3'))
		elif role != QtCore.Qt.DisplayRole:
			return QtCore.QVariant()

		return self.arraydata[index.row()][str(self.headerdata[index.column()])]

	def headerData(self, col, orientation=QtCore.Qt.Horizontal, role=QtCore.Qt.DisplayRole):
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole and len(self.headerdata) > 0:
			return QtCore.QVariant(self.headerdata[col])
		return QtCore.QVariant()

	def sort(self, Ncol, order):
		"""Sort table by given column number.
		"""
		self._parent._setSortCol(Ncol)
		self._parent._setSortOrder(order)

		self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
		self.arraydata = sorted(self.arraydata, key=operator.itemgetter(str(self.headerData(Ncol).toString())))
		if order == QtCore.Qt.DescendingOrder:
			self.arraydata.reverse()
		self.emit(QtCore.SIGNAL("layoutChanged()"))

class table(QtGui.QTableView):
	def __init__(self, parent, header, data, orderCol, orderWay):
		super (table, self).__init__ ()
		self._extraHeader = ['delete']
		self._parent = parent

		self.setSortingEnabled(True)
		self.setData(data, header)

		h = self.horizontalHeader()
		h.setSortIndicator(self._parent._orderCol, self._parent._orderWay)

	def setData(self, data, header):
		self.setHeader(header)

		for row in data:
			row['delete'] = 'delete Row'

		# set the table model
		tm = tableModel(data, self._header, self._parent)
		self.setModel(tm)
		self.model().sort(self._parent._orderCol, self._parent._orderWay)
		# hide vertical header
		self.verticalHeader().setVisible(False)
		self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

	def getData(self, row, col):
		#@TODO call a method from model to get this
		return self.model().arraydata[row][str(self.model().headerData(col).toString())]

	def setHeader(self, header):
		self._header = header + self._extraHeader

	def getColumnNameFromIndex(self, colIndex):
		return self.model().headerData(colIndex).toString()

	def getColumnIndexFromName(self, colName):
		return self._header.index(colName)

	def keyPressEvent(self, e):
		self._parent.keyPressEvent(e)



class menu(QtGui.QMenuBar):
	def __init__(self, window):
		super(menu, self).__init__(window)

		#exit action
		exitAction = QtGui.QAction(QtGui.QIcon(config.icons['app']), '&Exit', window)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip('Exit application')
		exitAction.triggered.connect(QtGui.qApp.quit)
		#new loan action
		newLoanAction = QtGui.QAction(QtGui.QIcon(config.icons['app']), '&New', window)
		newLoanAction.setStatusTip('Create new loan')
		newLoanAction.setShortcut('Ctrl+N')
		newLoanAction.triggered.connect(window._addNewLoan)
		#save loans action
		saveLoansAction = QtGui.QAction(QtGui.QIcon(config.icons['app']), '&Save loans', window)
		saveLoansAction.setStatusTip('Save loans to CSV')
		saveLoansAction.setShortcut('Ctrl+S')
		saveLoansAction.triggered.connect(window._saveLoans)

		fileMenu = self.addMenu('&File')
		fileMenu.addAction(exitAction)

		loansMenu = self.addMenu('&Loans')
		loansMenu.addAction(newLoanAction)
		loansMenu.addAction(saveLoansAction)
