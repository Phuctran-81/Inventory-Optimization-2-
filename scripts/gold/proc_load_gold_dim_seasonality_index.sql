/*
====================================================================
Insert data to gold.dim_seasonality_index table
====================================================================
*/
-- cte_seasonality_index calculates seasonality_index
WITH cte_seasonality_index AS (
	SELECT
		store_id,
		item_id,
		weekday_number,
		weekday_name,
		AVG (daily_vs_weekly_sales) AS seasonality_index
	FROM (
	-- This subquery calculate weekday sales vs average weekly sales ratio
			SELECT
				week_calendar,
				store AS store_id,
				item AS item_id,
				weekday_number,
				weekday_name,
				-- Calculate the ratio of each weekday sales with weekly average sales
				CAST (sales AS FLOAT) / AVG(sales) OVER (PARTITION BY store, item, week_calendar) AS daily_vs_weekly_sales
			FROM silver.train  )k
	GROUP BY store_id, item_id, weekday_number, weekday_name
			)
----------------------------------------------------------
  -- Insert Data to gold.dim_seasonality_index table
----------------------------------------------------------
INSERT INTO gold.dim_seasonality_index (
		seasonality_index_id,
		store_id,
		item_id,
		weekday_number,
		weekday_name,
		seasonality_index
				)
SELECT
	-- Create Primary Key for seasonality_index table
	ROW_NUMBER () OVER (ORDER BY store_id, item_id, weekday_number) AS seasonality_index_id,
	store_id,
	item_id,
	weekday_number,
	weekday_name,
	seasonality_index
FROM cte_seasonality_index
