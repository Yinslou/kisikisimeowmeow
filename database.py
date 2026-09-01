import sqlite3
from typing import Optional, Tuple

# Database initialization
def init_db():
    conn = sqlite3.connect('nutrition_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            budget REAL NOT NULL,
            allergens TEXT,
            goal TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# User data operations
def save_user_data(telegram_id: int, budget: float, allergens: Optional[str], goal: str):
    conn = sqlite3.connect('nutrition_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (telegram_id, budget, allergens, goal)
        VALUES (?, ?, ?, ?)
    ''', (telegram_id, budget, allergens, goal))
    conn.commit()
    conn.close()

def get_user_data(telegram_id: int) -> Tuple[float, Optional[str], str]:
    conn = sqlite3.connect('nutrition_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT budget, allergens, goal FROM users WHERE telegram_id = ?', (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (0.0, None, "")

# Initialize database on import
init_db()