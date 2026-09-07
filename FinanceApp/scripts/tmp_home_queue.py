import sqlite3

conn = sqlite3.connect('analysis/finance.db')
cur = conn.cursor()

print('home_top30')
rows = cur.execute(
    '''
    SELECT raw_description, COUNT(*) AS cnt,
           ROUND(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 2) AS spend
    FROM transactions
    WHERE source_institution = 'Amazon Detail'
      AND source_account = 'Item Purchases'
      AND normalized_category = 'Home'
    GROUP BY raw_description
    ORDER BY spend DESC, cnt DESC
    LIMIT 30
    '''
).fetchall()
for i, r in enumerate(rows, start=1):
    print(i, r)

print('---')
print('amazon_item_distribution')
dist = cur.execute(
    '''
    SELECT normalized_category, COUNT(*) AS cnt,
           ROUND(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 2) AS spend
    FROM transactions
    WHERE source_institution = 'Amazon Detail'
      AND source_account = 'Item Purchases'
    GROUP BY normalized_category
    ORDER BY cnt DESC
    '''
).fetchall()
for d in dist:
    print(d)
