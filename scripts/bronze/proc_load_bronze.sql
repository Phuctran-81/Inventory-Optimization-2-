BULK INSERT bronze.train
FROM 'C:\Users\phuct\OneDrive - VLG\Data Analyst\PROJECT\Retail Project\train.csv'
WITH (
		FIRSTROW = 2,
		FORMAT = 'CSV',
		FIELDQUOTE = '"',
		FIELDTERMINATOR = ',',
		ROWTERMINATOR = '0x0a',
		TABLOCK
		)
