# -*- coding: utf8 -*-

import Model


class model(Model.Model):
	fields = ['id_loan', 'lent_to', 'what', 'date_loan', 'date_return']

	@staticmethod
	def loadUnreturned():
		query = 'SELECT \
			*\
		FROM\
			loan\
		WHERE\
			date_return IS NULL\
		'
		return Model.Model.fetchAllRows(query)


class loan:
	exportFields = [item for item in model.fields if item != 'id_loan']

	@staticmethod
	def returnLoan(id):
		import datetime
		model.update({'date_return': datetime.date.today()}, ('id_loan = ?', [id]))
