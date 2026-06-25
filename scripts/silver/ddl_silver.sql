CREATE TABLE silver.train (
	record_id INT,
	date DATE,
	week_calendar DATE,
	store INT,
	item INT,
	sales INT,
	weekday_name NVARCHAR (50),
	weekday_number INT,
	dwh_create_date DATETIME2 DEFAULT GETDATE()
		)
