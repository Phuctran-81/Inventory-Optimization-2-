/*
====================================================================
Insert data to gold.dim_category table
====================================================================
*/
INSERT INTO gold.dim_category (
		category_id,
		store_id,
		item_id,
		running_pct,
		abc_category	
				)
-- this query calculates running contribute percent and categorizes products
SELECT
	ROW_NUMBER () OVER (ORDER BY store_id, item_id) AS category_id,
	store_id,
	item_id,
	running_pct,
	CASE 
		WHEN running_pct <= 0.8 THEN 'A'
		WHEN running_pct > 0.8 AND running_pct <= 0.95 THEN 'B'
		ELSE 'C'
	END AS abc_category
FROM (
	-- This Subquery calculates running_percent
	SELECT
		store_id,
		item_id,
		SUM (CAST (total_sales AS FLOAT)/ (SELECT SUM(sales) FROM silver.train)) OVER (ORDER BY total_sales DESC) AS running_pct
	FROM (
	-- This Subquery calculates the total sales of each item at each store
		SELECT
			store AS store_id,
			item AS item_id,
			SUM (sales) AS total_sales
		FROM silver.train
		GROUP BY store, item
				)t	
					)i
