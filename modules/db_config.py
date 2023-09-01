import sqlite3
import logging
import os  # import the os module

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DATABASE_NAME = 'callers.db'

def init_db():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS callers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT UNIQUE,
            voice_preference TEXT,
            email TEXT
        )
        ''')
        conn.commit()
        conn.close()
        logger.info("DB: Initialized the database successfully.")
    except Exception as e:
        logger.error(f"DB: Error occurred while initializing the database: {e}")
        raise e  # Optional, based on your error handling strategy
 


def save_caller(name, phone, voice_preference=None, email=None):
    try:
        conn = sqlite3.connect('callers.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM callers WHERE phone=?", (phone,))
        existing_caller = cursor.fetchone()

        if existing_caller:
            update_values = [name]
            query = "UPDATE callers SET name=?"
            
            if voice_preference:
                query += ", voice_preference=?"
                update_values.append(voice_preference)
            if email:
                query += ", email=?"
                update_values.append(email)
    
            query += " WHERE phone=?"
            update_values.append(phone)
            cursor.execute(query, update_values)
            logger.info(f"DB: Updated existing caller with phone: {phone} and name: {name}")

        else:
            query = "INSERT INTO callers (name, phone"
            placeholders = "?, ?"
            values = [name, phone]
    
            if voice_preference:
                query += ", voice_preference"
                values.append(voice_preference)
                placeholders += ", ?"
    
            if email:
                query += ", email"
                values.append(email)
                placeholders += ", ?"
    
            query += ") VALUES (" + placeholders + ")"
            cursor.execute(query, values)
            logger.info(f"DB: Saved new caller with phone: {phone} and name: {name}")
    
        conn.commit()
        conn.close()

    except Exception as e:
        logger.error(f"DB: Error occurred while saving/updating caller: {e}")
        raise e  # Optional

def get_caller(phone):
    try:
        conn = sqlite3.connect('callers.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM callers WHERE phone=?", (phone,))
        caller = cursor.fetchone()
        conn.close() 
        if caller:
            logger.info(f"DB: Retrieved data for {phone}: {caller}")
        else:
            logger.info(f"DB: No data found in DB for {phone}")
        return caller

    except Exception as e:
        logger.error(f"DB: Error occurred while retrieving caller for {phone}: {e}")
        raise e  # Optional

