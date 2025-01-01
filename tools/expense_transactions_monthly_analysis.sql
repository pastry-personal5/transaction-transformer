-- DELETE FROM expense_transactions_monthly_analysis;

DROP TABLE expense_transactions_monthly_analysis;


CREATE TABLE IF NOT EXISTS expense_transactions_monthly_analysis (
    user_identifier VARCHAR(128),
    month VARCHAR(7),          -- Stores the year and month (e.g., "2024-11")
    category0 VARCHAR(128),     -- Stores the category name
    total_sum DECIMAL(10, 0)   -- Stores the aggregated sum
)
CHARACTER SET utf8mb4;  -- Use utf8mb4 for better Unicode support

-- Insert data into monthly analysis table
INSERT INTO expense_transactions_monthly_analysis (user_identifier, month, category0, total_sum)
SELECT 
    u.user_identifier,                             -- User identifier
    m.month,                                       -- Month (Year-Month format)
    c.name AS category0,                           -- Category name from expense_categories
    COALESCE(SUM(t.amount), 0) AS total_sum        -- Total sum of amounts (0 if no transactions)
FROM
    (SELECT DISTINCT DATE_FORMAT(transaction_datetime, '%Y-%m') AS month
     FROM expense_transactions) AS m              -- Generate unique months from transactions
CROSS JOIN
    expense_categories AS c                        -- All categories
CROSS JOIN
    (SELECT DISTINCT user_identifier FROM expense_transactions) AS u -- All users
LEFT JOIN 
    expense_transactions AS t                      -- Join transactions
ON 
    t.category0 = c.name 
    AND DATE_FORMAT(t.transaction_datetime, '%Y-%m') = m.month
    AND t.user_identifier = u.user_identifier
GROUP BY 
    u.user_identifier, 
    m.month, 
    c.name;                                        -- Group by user, month, and category



