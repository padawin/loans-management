CREATE TABLE loan (
	id_loan INTEGER PRIMARY KEY AUTOINCREMENT,
	lent_to VARCHAR(255) NOT NULL,
	what TEXT NOT NULL,
	date_loan TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT 'NOW()'
);
