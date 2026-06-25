CREATE TABLE bronze.train (
	date	DATE,
	store	INT,
	item	INT,
	sales	FLOAT,
	dwh_create_date DATETIME2 DEFAULT GETDATE()
		);
