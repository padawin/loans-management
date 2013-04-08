# -*- coding: utf8 -*-

"""
Module to handle the GUI application
"""

from PyQt4 import QtCore
from PyQt4 import QtGui
import sys
import config
import operator
import csv


class application(QtGui.QApplication):
	"""
	Class for the application. it is here that the main window is created.
	"""

	_instance = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(application, cls).__new__(
								cls, *args, **kwargs)
		return cls._instance

	@classmethod
	def getInstance(cls):
		return cls._instance

	def __init__(self, data, headers):
		"""
		a(data, headers) -> loanGUI.application

		Construct of the class. Set the data and creates the main window.

		@param data list of elements to display in the table.
		@param headers titles of the table's columns.
		"""
		super(application, self).__init__(sys.argv)
		self.data = data
		self.headers = headers
		self.widget = mainWindow(self)

	def run(self):
		"""
		Execute the application
		"""
		return self.exec_()


class mainWindow(QtGui.QMainWindow):
	"""
	Class for the main window of the application.

	In this window will be listed the existing loans.
	"""

	def __init__(self, app):
		"""
		w(app) -> loanGUI.mainWindow

		Class's construct.

		@param app QtGui.QApplication Application containing the window.
		"""
		super(mainWindow, self).__init__()
		self._app = app
		(self._orderCol, self._orderWay) = (0, 1)
		#creation of the UI
		self.initUI()

	def initUI(self):
		"""
		Initialization of the UI:
		- creation of the menu bar,
		- creation of the status bar,
		- creation of the window's content,
		- definition of the window informations (size, position),
		- display of the window.
		"""
		#top menu
		self.setMenuBar(menu(self))
		self.setStatusBar(QtGui.QStatusBar())
		#creation fo the window
		self._create()
		#definition if window informations (size, position, title)
		self._setWindowInfos()
		#display the Whole Thing
		self.show()

	def _create(self):
		"""
		Method which create the UI
		The window elements are created here (table, button...)
		"""
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
		"""
		Displays a message in the status bar.
		"""
		self.statusBar().showMessage(text)

	def _setWindowInfos(self):
		"""
		Define window informations
		"""
		# default size
		self.setGeometry(300, 300, 600, 600)
		#~ self.setWidth()
		self.setWindowTitle('My loans')

	def _addNewLoan(self):
		pass

	def _saveLoans(self):
		"""
		Save the existing loans in a csv file, for backup purposes.
		"""
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
	"""
	Model associated to the QtGui.QTableView
	"""

	def __init__(self, data, headerdata, parent=None, *args):
		"""
		@param data a list of lists
		@param headerdata a list of strings
		"""
		QtCore.QAbstractTableModel.__init__(self, parent, *args)

		self._parent = parent
		self.arraydata = data
		self.headerdata = headerdata

	def rowCount(self, parent):
		"""
		Returns the number of rows in the table.
		"""
		return len(self.arraydata)

	def columnCount(self, parent):
		"""
		Returns the number of columns in the table.
		"""
		if len(self.arraydata) > 0:
			return len(self.arraydata[0])
		return 0

	def data(self, index, role):
		"""
		Apply some process to the data, from the given index and the given role.

		@param index current cell
		@role type of data access, can be QtCore.Qt.DisplayRole to display the
			data, QtCore.Qt.BackgroundRole to define the background color of
			the cell...
		"""
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
		"""
		Returns the information of the headers
		"""
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole and len(self.headerdata) > 0:
			return QtCore.QVariant(self.headerdata[col])
		return QtCore.QVariant()

	def sort(self, Ncol, order):
		"""
		Sort table by given column number.
		"""
		self._orderCol = Ncol
		self._orderWay = order

		self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
		self.arraydata = sorted(
			self.arraydata,
			key=operator.itemgetter(str(self.headerData(Ncol).toString()))
		)
		if order == QtCore.Qt.DescendingOrder:
			self.arraydata.reverse()
		self.emit(QtCore.SIGNAL("layoutChanged()"))


class table(QtGui.QTableView):
	"""
	Class to create a GUI table.
	"""

	def __init__(self, parent, header, data, orderCol, orderWay):
		"""
		Construct of the table.
		"""
		super(table, self).__init__()
		self._extraHeader = ['delete']
		self._parent = parent

		self.setSortingEnabled(True)
		self.setData(data, header)

		h = self.horizontalHeader()
		h.setSortIndicator(self._parent._orderCol, self._parent._orderWay)

	def setData(self, data, header):
		"""
		Define the model's data.
		"""
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
		"""
		Return the table data.
		"""
		return self.model().arraydata[row][str(self.model().headerData(col).toString())]

	def setHeader(self, header):
		"""
		Define the header, which will be the association of the object's extra
		header and the header given in argument. Used to add actions in the
		table.
		"""
		self._header = header + self._extraHeader

	def getColumnNameFromIndex(self, colIndex):
		"""
		Returns the name of a column.
		"""
		return self.model().headerData(colIndex).toString()

	def getColumnIndexFromName(self, colName):
		"""
		Returns the index of a column.
		"""
		return self._header.index(colName)

	def keyPressEvent(self, e):
		"""
		Handle the keypress event.
		"""
		self._parent.keyPressEvent(e)


class menu(QtGui.QMenuBar):
	"""
	Class to create the window's menu.
	"""

	def __init__(self, window):
		"""
		Construct of the menu. The menu's items are defined here.
		"""
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
