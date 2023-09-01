import sqlite3
import logging
import os  # import the os module
from flask import Blueprint, request
from twilio.twiml.voice_response import VoiceResponse
from modules.db_config import init_db, save_caller, get_caller

db_store_blueprint = Blueprint('db_store', __name__)

@db_store_blueprint.route("/store-name", methods=['POST'])
#@app.route("/store-name", methods=['POST'])
def store_name():
    try:
        caller_name = request.values.get('SpeechResult', '').strip()
        caller_number = request.values.get('From', 'Unknown')
        response = VoiceResponse()
        # Store the name to the DB
        save_name_to_db(caller_number, caller_name)
        response.say(f"Thanks, {caller_name}. Your name has been stored.", voice='Polly.Joanna')
        return str(response)

    except Exception as e:
        logger.error(f"Error occurred in store_data: {e}")
        response = VoiceResponse()
        response.say("Sorry, we encountered an error. Please try again.", voice='Polly.Joanna')
        return str(response)

def save_name_to_db(phone_number, name):
    # Check if the caller is already in the DB
    caller = get_caller(phone_number)
    if not caller:
        # Caller doesn't exist in the DB, save the new caller
        try:
            save_caller(name, phone_number)
            #logger.info(f"Stored the name {name} for the phone number {phone_number} in the database.")
        except Exception as e:
            logger.error(f"Error occurred while saving the name to the DB: {e}")
            # Handle exception, maybe retry or send an alert
    else:
        logger.info(f"Caller with phone number {phone_number} already exists in the database. Not saving again.")



 
