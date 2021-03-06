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
	tableFields = [item for item in model.fields if item not in ['date_return']]
	exportFields = [item for item in model.fields if item != 'id_loan']

	@staticmethod
	def returnLoan(id):
		import datetime
		model.update({'date_return': datetime.date.today()}, ('id_loan = ?', [id]))

	@staticmethod
	def getPeople():
		return [p['lent_to'] for p in model.loadAll(['lent_to'])]
