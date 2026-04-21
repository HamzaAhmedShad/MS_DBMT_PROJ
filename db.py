"""
db.py — MySQL connection and query helpers
for the Customer Segmentation Management System
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
import streamlit as st


def get_connection(host, user, password, database, port=3306):
    """Create and return a MySQL connection."""
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            autocommit=True
        )
        return conn
    except Error as e:
        return None


def run_query(conn, sql, params=None):
    """Execute a SELECT query and return a DataFrame."""
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return pd.DataFrame(rows) if rows else pd.DataFrame()
    except Error as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()


def run_write(conn, sql, params=None):
    """Execute INSERT / UPDATE / DELETE. Returns (success, lastrowid)."""
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        lid = cursor.lastrowid
        cursor.close()
        return True, lid
    except Error as e:
        st.error(f"Write error: {e}")
        return False, None


# ── KPI helpers ───────────────────────────────────────────────────────────────

def kpi_total_customers(conn):
    df = run_query(conn, "SELECT COUNT(*) AS n FROM CUSTOMERS")
    return int(df["n"].iloc[0]) if not df.empty else 0

def kpi_total_products(conn):
    df = run_query(conn, "SELECT COUNT(*) AS n FROM PRODUCTS")
    return int(df["n"].iloc[0]) if not df.empty else 0

def kpi_total_revenue(conn):
    df = run_query(conn, "SELECT COALESCE(SUM(TotalAmount),0) AS n FROM TRANSACTIONS")
    return float(df["n"].iloc[0]) if not df.empty else 0.0

def kpi_total_transactions(conn):
    df = run_query(conn, "SELECT COUNT(*) AS n FROM TRANSACTIONS")
    return int(df["n"].iloc[0]) if not df.empty else 0

def kpi_avg_order_value(conn):
    df = run_query(conn, "SELECT COALESCE(AVG(TotalAmount),0) AS n FROM TRANSACTIONS")
    return float(df["n"].iloc[0]) if not df.empty else 0.0

def kpi_segments(conn):
    df = run_query(conn, "SELECT COUNT(DISTINCT SegmentLabel) AS n FROM SEGMENTATION_RESULTS")
    return int(df["n"].iloc[0]) if not df.empty else 0


# ── Chart data ────────────────────────────────────────────────────────────────

def chart_monthly_revenue(conn):
    return run_query(conn, """
        SELECT DATE_FORMAT(TransactionDate, '%Y-%m') AS Month,
               SUM(TotalAmount) AS Revenue,
               COUNT(*) AS Transactions
        FROM TRANSACTIONS
        GROUP BY Month ORDER BY Month
    """)

def chart_category_revenue(conn):
    return run_query(conn, """
        SELECT p.Category, SUM(t.TotalAmount) AS Revenue
        FROM PRODUCTS p JOIN TRANSACTIONS t ON p.ProductID = t.ProductID
        GROUP BY p.Category ORDER BY Revenue DESC
    """)

def chart_segment_distribution(conn):
    return run_query(conn, """
        SELECT SegmentLabel, COUNT(*) AS Customers
        FROM SEGMENTATION_RESULTS
        GROUP BY SegmentLabel
    """)

def chart_top_customers(conn, n=8):
    return run_query(conn, f"""
        SELECT CONCAT(c.FirstName,' ',c.LastName) AS Customer,
               SUM(t.TotalAmount) AS TotalSpent
        FROM CUSTOMERS c JOIN TRANSACTIONS t ON c.CustomerID = t.CustomerID
        GROUP BY c.CustomerID, c.FirstName, c.LastName
        ORDER BY TotalSpent DESC LIMIT {n}
    """)

def chart_rfm(conn):
    return run_query(conn, """
        SELECT CONCAT(c.FirstName,' ',c.LastName) AS Customer,
               bm.RecencyOfPurchase AS Recency,
               bm.PurchaseFrequency AS Frequency,
               bm.AverageSpending   AS Monetary,
               sr.SegmentLabel
        FROM CUSTOMERS c
        JOIN BEHAVIORAL_METRICS bm ON c.CustomerID = bm.CustomerID
        JOIN SEGMENTATION_RESULTS sr ON c.CustomerID = sr.CustomerID
    """)

def chart_products_revenue(conn):
    return run_query(conn, """
        SELECT p.ProductName, SUM(t.TotalAmount) AS Revenue
        FROM PRODUCTS p JOIN TRANSACTIONS t ON p.ProductID = t.ProductID
        GROUP BY p.ProductName ORDER BY Revenue DESC LIMIT 10
    """)


# ── CRUD — Customers ──────────────────────────────────────────────────────────

def get_all_customers(conn):
    return run_query(conn, "SELECT * FROM CUSTOMERS ORDER BY CustomerID")

def get_customer(conn, cid):
    return run_query(conn, "SELECT * FROM CUSTOMERS WHERE CustomerID = %s", (cid,))

def add_customer(conn, first, last, age, gender, email, phone, reg_date):
    return run_write(conn, """
        INSERT INTO CUSTOMERS (FirstName,LastName,Age,Gender,Email,Phone,RegistrationDate)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (first, last, age if age else None, gender, email, phone, reg_date))

def update_customer(conn, cid, first, last, age, gender, email, phone, reg_date):
    return run_write(conn, """
        UPDATE CUSTOMERS SET FirstName=%s, LastName=%s, Age=%s, Gender=%s,
        Email=%s, Phone=%s, RegistrationDate=%s WHERE CustomerID=%s
    """, (first, last, age if age else None, gender, email, phone, reg_date, cid))

def delete_customer(conn, cid):
    return run_write(conn, "DELETE FROM CUSTOMERS WHERE CustomerID = %s", (cid,))


# ── CRUD — Products ───────────────────────────────────────────────────────────

def get_all_products(conn):
    return run_query(conn, "SELECT * FROM PRODUCTS ORDER BY ProductID")

def add_product(conn, name, category, price):
    return run_write(conn, """
        INSERT INTO PRODUCTS (ProductName, Category, Price) VALUES (%s,%s,%s)
    """, (name, category, price))

def update_product(conn, pid, name, category, price):
    return run_write(conn, """
        UPDATE PRODUCTS SET ProductName=%s, Category=%s, Price=%s WHERE ProductID=%s
    """, (name, category, price, pid))

def delete_product(conn, pid):
    return run_write(conn, "DELETE FROM PRODUCTS WHERE ProductID = %s", (pid,))


# ── CRUD — Transactions ───────────────────────────────────────────────────────

def get_all_transactions(conn):
    return run_query(conn, """
        SELECT t.TransactionID,
               CONCAT(c.FirstName,' ',c.LastName) AS Customer,
               p.ProductName, p.Category,
               t.TransactionDate, t.Quantity, t.TotalAmount
        FROM TRANSACTIONS t
        JOIN CUSTOMERS c ON t.CustomerID = c.CustomerID
        JOIN PRODUCTS  p ON t.ProductID  = p.ProductID
        ORDER BY t.TransactionDate DESC
    """)

def add_transaction(conn, cid, pid, date, qty, total):
    return run_write(conn, """
        INSERT INTO TRANSACTIONS (CustomerID,ProductID,TransactionDate,Quantity,TotalAmount)
        VALUES (%s,%s,%s,%s,%s)
    """, (cid, pid, date, qty, total))

def delete_transaction(conn, tid):
    return run_write(conn, "DELETE FROM TRANSACTIONS WHERE TransactionID = %s", (tid,))


# ── CRUD — Behavioral Metrics ─────────────────────────────────────────────────

def get_all_metrics(conn):
    return run_query(conn, """
        SELECT c.CustomerID, CONCAT(c.FirstName,' ',c.LastName) AS Customer,
               bm.PurchaseFrequency, bm.AverageSpending, bm.RecencyOfPurchase
        FROM BEHAVIORAL_METRICS bm
        JOIN CUSTOMERS c ON bm.CustomerID = c.CustomerID
        ORDER BY bm.AverageSpending DESC
    """)

def upsert_metrics(conn, cid, freq, avg_spend, recency):
    return run_write(conn, """
        INSERT INTO BEHAVIORAL_METRICS (CustomerID, PurchaseFrequency, AverageSpending, RecencyOfPurchase)
        VALUES (%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            PurchaseFrequency=VALUES(PurchaseFrequency),
            AverageSpending=VALUES(AverageSpending),
            RecencyOfPurchase=VALUES(RecencyOfPurchase)
    """, (cid, freq, avg_spend, recency))


# ── CRUD — Segmentation Results ───────────────────────────────────────────────

def get_all_segments(conn):
    return run_query(conn, """
        SELECT sr.SegmentationID,
               CONCAT(c.FirstName,' ',c.LastName) AS Customer,
               sr.CustomerID, sr.ClusterID, sr.SegmentLabel, sr.SegmentationDate
        FROM SEGMENTATION_RESULTS sr
        JOIN CUSTOMERS c ON sr.CustomerID = c.CustomerID
        ORDER BY sr.SegmentationDate DESC, sr.ClusterID
    """)

def add_segment(conn, cid, cluster_id, label, date):
    return run_write(conn, """
        INSERT INTO SEGMENTATION_RESULTS (CustomerID, ClusterID, SegmentLabel, SegmentationDate)
        VALUES (%s,%s,%s,%s)
    """, (cid, cluster_id, label, date))

def delete_segment(conn, sid):
    return run_write(conn, "DELETE FROM SEGMENTATION_RESULTS WHERE SegmentationID = %s", (sid,))


# ── Analytical Queries (Query Pack) ──────────────────────────────────────────

QUERIES = {
    "Q01 – Full Transaction History": (
        "Basic",
        "All transactions showing customer name, product, category, quantity, and amount.",
        """
SELECT t.TransactionID, t.TransactionDate,
       CONCAT(c.FirstName,' ',c.LastName) AS CustomerName,
       p.ProductName, p.Category, t.Quantity, t.TotalAmount
FROM TRANSACTIONS t
JOIN CUSTOMERS c ON t.CustomerID = c.CustomerID
JOIN PRODUCTS  p ON t.ProductID  = p.ProductID
ORDER BY t.TransactionDate DESC
"""
    ),
    "Q02 – Customer Segmentation Profiles": (
        "Basic",
        "Each customer with their assigned cluster and segment label.",
        """
SELECT c.CustomerID, CONCAT(c.FirstName,' ',c.LastName) AS CustomerName,
       c.Age, c.Gender, sr.ClusterID, sr.SegmentLabel, sr.SegmentationDate
FROM CUSTOMERS c
JOIN SEGMENTATION_RESULTS sr ON c.CustomerID = sr.CustomerID
ORDER BY sr.ClusterID, c.LastName
"""
    ),
    "Q03 – Home Decor Transactions": (
        "Basic",
        "Filter transactions to only Home Decor category products.",
        """
SELECT t.TransactionID, CONCAT(c.FirstName,' ',c.LastName) AS CustomerName,
       p.ProductName, t.Quantity, t.TotalAmount, t.TransactionDate
FROM TRANSACTIONS t
JOIN CUSTOMERS c ON t.CustomerID = c.CustomerID
JOIN PRODUCTS  p ON t.ProductID  = p.ProductID
WHERE p.Category = 'Home Decor'
ORDER BY t.TotalAmount DESC
"""
    ),
    "Q04 – Customers with Behavioral Metrics": (
        "Basic",
        "LEFT JOIN showing customers alongside their behavioral summary (NULLs where no metrics exist).",
        """
SELECT c.CustomerID, CONCAT(c.FirstName,' ',c.LastName) AS CustomerName,
       c.Email, bm.PurchaseFrequency, bm.AverageSpending, bm.RecencyOfPurchase
FROM CUSTOMERS c
LEFT JOIN BEHAVIORAL_METRICS bm ON c.CustomerID = bm.CustomerID
ORDER BY bm.AverageSpending DESC
"""
    ),
    "Q05 – Products Sorted by Price": (
        "Basic",
        "All products ordered from most to least expensive.",
        "SELECT ProductID, ProductName, Category, Price FROM PRODUCTS ORDER BY Price DESC"
    ),
    "Q06 – Transactions in 2024": (
        "Basic",
        "All transactions that occurred in the year 2024.",
        """
SELECT t.TransactionID, CONCAT(c.FirstName,' ',c.LastName) AS CustomerName,
       p.ProductName, t.TransactionDate, t.Quantity, t.TotalAmount
FROM TRANSACTIONS t
JOIN CUSTOMERS c ON t.CustomerID = c.CustomerID
JOIN PRODUCTS  p ON t.ProductID  = p.ProductID
WHERE t.TransactionDate BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY t.TransactionDate
"""
    ),
    "Q07 – Products Never Purchased": (
        "Basic",
        "Products with no transaction records (anti-join using LEFT JOIN + NULL filter).",
        """
SELECT p.ProductID, p.ProductName, p.Category, p.Price
FROM PRODUCTS p
LEFT JOIN TRANSACTIONS t ON p.ProductID = t.ProductID
WHERE t.TransactionID IS NULL
"""
    ),
    "Q08 – Revenue per Customer": (
        "Intermediate",
        "GROUP BY aggregating total spend, transaction count, and last purchase per customer.",
        """
SELECT c.CustomerID, CONCAT(c.FirstName,' ',c.LastName) AS CustomerName,
       COUNT(t.TransactionID) AS TotalTransactions,
       SUM(t.TotalAmount) AS TotalSpent,
       AVG(t.TotalAmount) AS AvgOrderValue,
       MAX(t.TransactionDate) AS LastPurchase
FROM CUSTOMERS c
JOIN TRANSACTIONS t ON c.CustomerID = t.CustomerID
GROUP BY c.CustomerID, c.FirstName, c.LastName
ORDER BY TotalSpent DESC
"""
    ),
    "Q09 – Revenue by Category": (
        "Intermediate",
        "GROUP BY category showing unique customers, units sold, and total revenue.",
        """
SELECT p.Category,
       COUNT(DISTINCT t.CustomerID) AS UniqueCustomers,
       SUM(t.Quantity) AS TotalUnitsSold,
       SUM(t.TotalAmount) AS TotalRevenue,
       ROUND(AVG(t.TotalAmount),2) AS AvgOrderValue
FROM PRODUCTS p
JOIN TRANSACTIONS t ON p.ProductID = t.ProductID
GROUP BY p.Category
ORDER BY TotalRevenue DESC
"""
    ),
    "Q10 – High-Value Customers (>$70)": (
        "Intermediate",
        "HAVING clause filtering customers whose total lifetime spend exceeds $70.",
        """
SELECT c.CustomerID, CONCAT(c.FirstName,' ',c.LastName) AS CustomerName,
       COUNT(t.TransactionID) AS NumTransactions,
       SUM(t.TotalAmount) AS TotalSpent
FROM CUSTOMERS c
JOIN TRANSACTIONS t ON c.CustomerID = t.CustomerID
GROUP BY c.CustomerID, c.FirstName, c.LastName
HAVING TotalSpent > 70
ORDER BY TotalSpent DESC
"""
    ),
    "Q11 – Above-Average Spenders (Subquery)": (
        "Intermediate",
        "Subquery in HAVING dynamically compares each customer's total to the overall average.",
        """
SELECT c.CustomerID, CONCAT(c.FirstName,' ',c.LastName) AS CustomerName,
       SUM(t.TotalAmount) AS TotalSpent
FROM CUSTOMERS c
JOIN TRANSACTIONS t ON c.CustomerID = t.CustomerID
GROUP BY c.CustomerID, c.FirstName, c.LastName
HAVING TotalSpent > (
    SELECT AVG(sub.CustomerTotal) FROM (
        SELECT SUM(TotalAmount) AS CustomerTotal
        FROM TRANSACTIONS GROUP BY CustomerID
    ) sub
)
ORDER BY TotalSpent DESC
"""
    ),
    "Q12 – Segmentation RFM Summary": (
        "Intermediate",
        "Per-segment averages for recency, frequency, and monetary value from BEHAVIORAL_METRICS.",
        """
SELECT sr.SegmentLabel, COUNT(sr.CustomerID) AS NumCustomers,
       ROUND(AVG(bm.RecencyOfPurchase),1) AS Avg_Recency_Days,
       ROUND(AVG(bm.PurchaseFrequency),1) AS Avg_Frequency,
       ROUND(AVG(bm.AverageSpending),2)   AS Avg_MonetaryValue
FROM SEGMENTATION_RESULTS sr
JOIN BEHAVIORAL_METRICS bm ON sr.CustomerID = bm.CustomerID
GROUP BY sr.SegmentLabel
ORDER BY Avg_MonetaryValue DESC
"""
    ),
    "Q13 ⭐ Running Total Revenue (Window)": (
        "Advanced",
        "SUM() window function computing cumulative revenue ordered by transaction date.",
        """
SELECT t.TransactionID, t.TransactionDate,
       CONCAT(c.FirstName,' ',c.LastName) AS CustomerName,
       p.ProductName, t.TotalAmount,
       SUM(t.TotalAmount) OVER (
           ORDER BY t.TransactionDate
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS RunningTotal
FROM TRANSACTIONS t
JOIN CUSTOMERS c ON t.CustomerID = c.CustomerID
JOIN PRODUCTS  p ON t.ProductID  = p.ProductID
ORDER BY t.TransactionDate
"""
    ),
    "Q14 ⭐ Top Product per Category (RANK)": (
        "Advanced",
        "RANK() with PARTITION BY to find the best-selling product in each category.",
        """
SELECT Category, ProductName, TotalRevenue, TotalUnitsSold FROM (
    SELECT p.Category, p.ProductName,
           SUM(t.TotalAmount) AS TotalRevenue,
           SUM(t.Quantity)    AS TotalUnitsSold,
           RANK() OVER (PARTITION BY p.Category ORDER BY SUM(t.TotalAmount) DESC) AS rnk
    FROM PRODUCTS p JOIN TRANSACTIONS t ON p.ProductID = t.ProductID
    GROUP BY p.Category, p.ProductName
) ranked WHERE rnk = 1 ORDER BY TotalRevenue DESC
"""
    ),
    "Q15 ⭐ Customer LTV with Segmentation (CTE)": (
        "Advanced",
        "CTE computes lifetime value per customer, then joins segmentation for full context.",
        """
WITH CustomerLTV AS (
    SELECT c.CustomerID,
           CONCAT(c.FirstName,' ',c.LastName) AS CustomerName,
           COUNT(t.TransactionID)             AS TotalOrders,
           SUM(t.TotalAmount)                 AS LifetimeValue,
           ROUND(AVG(t.TotalAmount),2)        AS AvgOrderValue,
           DATEDIFF(CURDATE(), MAX(t.TransactionDate)) AS DaysSinceLastOrder
    FROM CUSTOMERS c JOIN TRANSACTIONS t ON c.CustomerID = t.CustomerID
    GROUP BY c.CustomerID, c.FirstName, c.LastName
)
SELECT ltv.CustomerID, ltv.CustomerName, ltv.TotalOrders,
       ltv.LifetimeValue, ltv.AvgOrderValue, ltv.DaysSinceLastOrder,
       sr.SegmentLabel
FROM CustomerLTV ltv
JOIN SEGMENTATION_RESULTS sr ON ltv.CustomerID = sr.CustomerID
ORDER BY ltv.LifetimeValue DESC
"""
    ),
}
