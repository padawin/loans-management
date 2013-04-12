# -*- coding: utf8 -*-

import Model


class loan:
	pass


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
