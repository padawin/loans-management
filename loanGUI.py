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
import loan


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

	def returnRow(self, idRow):
		"""
		a.returnRow(idRow)

		Flag a row as returned. Will not be displayed anymore

		@param idRow integer id of the row to return
		"""

		loan.loan.returnLoan(idRow)
		self.refreshData()

	def addRows(self, data):
		"""
		a.addRows(data)

		Add a collection of rows in the database and refresh the display

		@param data list rows to add in the database
		"""
		for r in data:
			loan.model.insert(r)
		self.refreshData()

	def refreshData(self):
		self.data = loan.model.loadUnreturned()
		self.widget.table.setData(self.data)


class mainWindow(QtGui.QMainWindow):
	"""
	Class for the main window of the application.

	In this window will be listed the existing loans.
	"""

	_instance = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(mainWindow, cls).__new__(
								cls, *args, **kwargs)
		return cls._instance

	@classmethod
	def getInstance(cls):
		return cls._instance

	def __init__(self, app):
		"""
		w(app) -> loanGUI.mainWindow

		Class's construct.

		@param app QtGui.QApplication Application containing the window.
		"""
		super(mainWindow, self).__init__()
		self._app = app
		self.addWidget = None
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

		self.table = table(self, self._app.headers, self._app.data, self._orderCol, self._orderWay)
		vbox.addWidget(self.table)
		newLoanFieldButton = QtGui.QPushButton('Add Loan')
		#button event
		newLoanFieldButton.clicked.connect(self.addNewLoan)
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

	def addNewLoan(self):
		if self.addWidget is None:
			self.addWidget = addLoan(self._app)
		self.addWidget.show()

	def saveLoans(self):
		"""
		Save the existing loans in a csv file, for backup purposes.
		"""
		if len(self._app.data) == 0:
			self.displayMessage("No loan to save")
			return

		fileName = QtCore.QDir.home().absolutePath() + QtCore.QDir.separator() + ("loans.csv")

		csvData = list()
		for i in self._app.data:
			row = {k: i[k] for k in loan.loan.exportFields}
			for k in row:
				try:
					row[k] = row[k].encode('utf-8')
				except:
					row[k] = '' if row[k] is None else str(row[k])
			csvData.append(row)

		writer = csv.DictWriter(open(fileName, "wb"), row.keys())
		writer.writeheader()
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
			return None
		elif role == QtCore.Qt.ForegroundRole:
			return QtGui.QColor('#073642')
		elif role == QtCore.Qt.BackgroundRole:
			return QtGui.QColor('#fdf6e3')
		elif role != QtCore.Qt.DisplayRole:
			return None

		return self.arraydata[index.row()][str(self.headerdata[index.column()])]

	def headerData(self, col, orientation=QtCore.Qt.Horizontal, role=QtCore.Qt.DisplayRole):
		"""
		Returns the information of the headers
		"""
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole and len(self.headerdata) > 0:
			return self.headerdata[col]
		return None

	def sort(self, Ncol, order):
		"""
		Sort table by given column number.
		"""
		self._orderCol = Ncol
		self._orderWay = order

		self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
		self.arraydata = sorted(
			self.arraydata,
			key=operator.itemgetter(str(self.headerData(Ncol)))
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
		self._extraHeader = ['return']
		self._parent = parent

		self.setSortingEnabled(True)
		self.setData(data, header)

		h = self.horizontalHeader()
		h.setSortIndicator(self._parent._orderCol, self._parent._orderWay)

	def setData(self, data, header=None):
		"""
		Define the model's data.
		"""
		if header is not None:
			self.setHeader(header)

		import copy
		d = copy.copy(data)
		returnLabel = 'Return';
		for key, row in enumerate(d):
			row = {k: row[k] for k in loan.loan.tableFields}
			row['return'] = returnLabel
			d[key] = row

		self.setItemDelegateForColumn(4, returnButtonDelegate(self, returnLabel, 4))

		# set the table model
		tm = tableModel(d, self._header, self._parent)
		self.setModel(tm)
		self.model().sort(self._parent._orderCol, self._parent._orderWay)
		# hide vertical header
		self.verticalHeader().setVisible(False)
		self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

	def getData(self, row, col):
		"""
		Return the table data.
		"""
		return self.model().arraydata[row][str(self.model().headerData(col))]

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
		newLoanAction = QtGui.QAction(QtGui.QIcon(config.icons['app']), '&Create new loan', window)
		newLoanAction.setStatusTip('Create new loan')
		newLoanAction.setShortcut('Ctrl+N')
		newLoanAction.triggered.connect(window.addNewLoan)
		#save loans action
		saveLoansAction = QtGui.QAction(QtGui.QIcon(config.icons['app']), '&Save loans', window)
		saveLoansAction.setStatusTip('Save loans to CSV')
		saveLoansAction.setShortcut('Ctrl+S')
		saveLoansAction.triggered.connect(window.saveLoans)

		fileMenu = self.addMenu('&File')
		fileMenu.addAction(exitAction)

		loansMenu = self.addMenu('&Loans')
		loansMenu.addAction(newLoanAction)
		loansMenu.addAction(saveLoansAction)


class returnButtonDelegate(QtGui.QItemDelegate):
	"""
	Class to create a button to be used in the table.
	"""

	def __init__(self, parent, label, columnIndex):
		"""
		Construct, set the button's label.
		"""
		QtGui.QItemDelegate.__init__(self, parent)
		self.label = label
		self.columnIndex = columnIndex

	def paint(self, painter, option, index):
		"""
		Displays the button in the good cell.
		"""
		self.index = index
		button = self._getButton(self.parent().getData(index.row(), self.columnIndex))

		if not self.parent().indexWidget(index):
			self.parent().setIndexWidget(index, button)

	def _getButton(self, running):
		"""
		d._getButton(running) -> QtGui.QPushButton

		Create the button widget

		@param running

		@return QtGui.QPushButton
		"""
		return QtGui.QPushButton(
			self.label,
			self.parent(),
			clicked=self.returnButtonClicked
		)

	def returnButtonClicked(self, row):
		"""
		Action to execute when the button is pressed.
		It'll ask a confirmation to the user to return the corresponding row.
		"""
		if QtGui.QMessageBox.warning(
				self.parent(),
				"Delete loan",
				"Did you get back this item ?",
				"Yes", "No", '',
				1, 1) == 0:
			application.getInstance().returnRow(self.parent().getData(self.index.row(), 0))


class addLoan(QtGui.QWidget):
	"""
	Widget containing a form to add some loans
	"""

	_instance = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(addLoan, cls).__new__(
								cls, *args, **kwargs)
		return cls._instance

	@classmethod
	def getInstance(cls):
		return cls._instance

	def __init__(self, app):
		"""
		Construct. Set the app, create the UI and define some informations
		for the window (such as its size and position).
		"""
		super(addLoan, self).__init__()
		self._app = app
		self.initUI()
		self._setWindowInfos()

	def initUI(self):
		"""
		Create the widget's UI.
		"""

		#~ initialization of the layout
		self.layout = QtGui.QGridLayout()

		#~ Creation of the fields (labels, fields, errors labels)
		whoLabel = QtGui.QLabel('Who ?')
		self.whoField = QtGui.QLineEdit()
		self.whoErrorLabel = QtGui.QLabel()
		self.whoErrorLabel.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		self.updateCompleter()

		whatLabel = QtGui.QLabel('What ?')
		self.whatField = QtGui.QTextEdit()
		self.whatErrorLabel = QtGui.QLabel()
		self.whatErrorLabel.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

		whenLabel = QtGui.QLabel('When ?')
		self.whenField = QtGui.QDateEdit(QtCore.QDate.currentDate())
		self.whenField.setDisplayFormat('yyyy-MM-dd')
		self.whenField.setCalendarPopup(True)
		self.whenErrorLabel = QtGui.QLabel()
		self.whenErrorLabel.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

		#~ Creation of the buttons
		self.cancelButton = QtGui.QPushButton('cancel')
		self.addButton = QtGui.QPushButton('Add')
		self.cancelButton.clicked.connect(self.closeWindow)
		self.addButton.clicked.connect(self.addLoanAction)

		#~ The elements are added here in the layout
		#~ With the gridlayout, the elements are added to specific coordinates
		#~ in the grid (arguments 2 and 3 of the addWidget method), and are
		#~ defined to fill a specific space (arguments 4 and 5 of the addWidget
		#~ method)
		self.layout.addWidget(whoLabel, 1, 0)
		self.layout.addWidget(self.whoField, 1, 1, 1, 2)
		self.layout.addWidget(self.whoErrorLabel, 1, 4)
		self.layout.addWidget(whatLabel, 2, 0)
		self.layout.addWidget(self.whatField, 2, 1, 1, 2)
		self.layout.addWidget(self.whatErrorLabel, 2, 4)
		self.layout.addWidget(whenLabel, 3, 0)
		self.layout.addWidget(self.whenField, 3, 1, 1, 2)
		self.layout.addWidget(self.whenErrorLabel, 3, 4)
		self.layout.addWidget(self.cancelButton, 4, 1)
		self.layout.addWidget(self.addButton, 4, 2)

		#~ Definition of the widget's layout
		self.setLayout(self.layout)

	def _setWindowInfos(self):
		"""
		Definition of the window's informations
		"""
		self.setGeometry(0, 0, 400, 300)
		self.setFixedSize(400, 300)
		resolution = QtGui.QDesktopWidget().screenGeometry()
		self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
				  (resolution.height() / 2) - (self.frameSize().height() / 2))

		self.setWindowTitle('Add loan')

	def addLoanAction(self):
		"""
		Method executed when the addLoan button is pressed.
		It cleans and checks the parameters before trying to insert
		them through the loan.model.
		"""
		import re
		who = str(self.whoField.text()).strip()
		when = str(self.whenField.text())
		what = self.whatField.toPlainText()
		objects = re.split(',|\n', self.whatField.toPlainText())
		data = [{'what': str(w).strip(), 'lent_to': who, 'date_loan': when} for w in objects if str(w).strip() != '']

		if self.handleErrors({'who': who, 'what': what}):
			self._app.addRows(data)
			self.updateCompleter()
			self.closeWindow()

	def handleErrors(self, fields):
		"""
		w.handleErrors(fields) -> bool

		Check if the fields's values are correct.
		If a field is incorrect, a message is added in its corresponding
		error label.

		@param fields dict of the fields to check

		@return bool True if there is no error, False else
		"""
		valid = True
		if len(fields['who']) == 0:
			self.whoErrorLabel.setText('A value is expected')
			valid = False
		else:
			self.whoErrorLabel.clear()
		if len(fields['what']) == 0:
			self.whatErrorLabel.setText('A value is expected')
			valid = False
		else:
			self.whatErrorLabel.clear()
		return valid

	def keyPressEvent(self, e):
		"""
		Handle keyboard events on the widget.
		"""
		if e.key() == QtCore.Qt.Key_Escape:
			self.closeWindow()

	def closeWindow(self):
		"""
		Empties the fields and error labels before closing the widget.
		"""
		self.whoField.setText('')
		self.whenField.setDate(QtCore.QDate.currentDate())
		self.whatField.setText('')
		self.whoErrorLabel.clear()
		self.whatErrorLabel.clear()
		self.close()

	def updateCompleter(self):
		completerList = QtCore.QStringList()
		for i in loan.loan.getPeople():
			completerList.append(QtCore.QString(i))
		lineEditCompleter = QtGui.QCompleter(completerList)
		lineEditCompleter.setCompletionMode(QtGui.QCompleter.InlineCompletion)
		lineEditCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

		self.whoField.setCompleter(lineEditCompleter)
