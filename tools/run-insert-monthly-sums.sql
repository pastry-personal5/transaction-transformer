CREATE TABLE IF NOT EXISTS expense_transactions_monthly_analysis (
    month VARCHAR(7),          -- Stores the year and month (e.g., "2024-11")
    category0 VARCHAR(128),     -- Stores the category name
    total_sum DECIMAL(10, 0)   -- Stores the aggregated sum
)
CHARACTER SET utf8mb4;  -- Use utf8mb4 for better Unicode support

-- Define a delimiter to handle the procedure definition
DELIMITER $$

-- Create the stored procedure to insert monthly sums into the table
CREATE PROCEDURE InsertMonthlySums()
BEGIN
    -- Insert grouped data into the target table
    INSERT INTO expense_transactions_monthly_analysis (month, category0, total_sum)
    SELECT
        DATE_FORMAT(s.transaction_datetime, '%Y-%m') AS month, -- Extract year-month
        s.category0,                                           -- Category
        SUM(s.amount) AS total_sum                             -- Sum of values
    FROM
        expense_transactions AS s
    GROUP BY
        DATE_FORMAT(s.transaction_datetime, '%Y-%m'),          -- Group by formatted month
        s.category0;                                           -- Group by category
END $$

-- Reset the delimiter back to semicolon
DELIMITER ;

-- Check if event scheduler is enabled
SHOW VARIABLES LIKE 'event_scheduler';

-- If it is OFF, you can enable it with the following command
SET GLOBAL event_scheduler = ON;

CREATE EVENT IF NOT EXISTS run_insert_monthly_sums
ON SCHEDULE EVERY 1 DAY
STARTS '2024-12-01 00:00:00'  -- Start the event at midnight
DO
    CALL InsertMonthlySums();

show EVENTS;
