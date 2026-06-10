import sqlite3
import sys

def main():
    conn = sqlite3.connect('system.db')
    cursor = conn.cursor()
    cursor.execute('SELECT category, COUNT(*) FROM accounts GROUP BY category')
    rows = cursor.fetchall()
    
    # Sort by count descending
    rows.sort(key=lambda x: x[1], reverse=True)
    
    with open('category_stats.txt', 'w', encoding='utf-8') as f:
        f.write("Category Stats:\n")
        f.write("-" * 30 + "\n")
        for cat, count in rows:
            f.write(f"{cat}: {count}\n")
    
    conn.close()

if __name__ == "__main__":
    main()
