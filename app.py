""" This is currently in develepment mode and still needs to be orginized. This will still work 
    I am currently using this for chatCPT develepment """

import os
import sqlite3
import logging
import openai
import random #Random Choices for IVR.

from flask import Flask, session, request, current_app
from datetime import datetime, timedelta
from flask_session import Session
from twilio.twiml.voice_response import Gather, VoiceResponse
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
from modules.calendar_module import create_appointment
from modules.email_module import send_email
from modules.db_config import init_db, save_caller, get_caller
from config import Config, gpt3Msg
from modules import db_store

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config) #Load config.py file 
app.register_blueprint(db_store.db_store_blueprint) # Load DBStore.py file
Session(app)

# This will check if the database exists, and if not, will call init_db
if not os.path.exists("callers.db"):
    logger.info("DB: callers.db does not exist. Initializing database...")
    init_db()

#from voice_routes import *
@app.route("/voice", methods=['GET', 'POST']) 
def voice():
    response = VoiceResponse()
    caller_phone_number = request.form.get('From')
    caller = get_caller(caller_phone_number)
    session['caller_phone_number'] = caller_phone_number  # Store the phone number in session    

    #caller = get_caller(caller_phone_number)
        
    if caller:
        caller_name = caller[1]  # Assuming 'name' is the second column in your database
        message = f"Hello, {caller_name}! Welcome to MY_COMAPNY_NAME. How can i help you today? You can say view my accounts, Connect me to an agent, or even ask me anything about MY_COMAPNY_NAME. Fun fact, i am a new AI made by MY_COMAPNY_NAME."
        with response.gather(input="speech", action='/handle-input', method='POST', timeout=5) as gather:
            gather.say(message, voice='Polly.Matthew')
        response.say("Oops, my circuits must've blinked. Can you repeat that?", voice='Polly.Joanna')
        return str(response)
    else:
    
    
        message = gpt3Msg.Message

        #message = ("Hello! Welcome to MY_COMAPNY_NAME. Quick note: I'm the new digital kid on the block. "
        #           "Think of me as the chatbot version of baby Yoda, powered by GPT. "
        #           "How can I assist you today?")
    
    # If no Response then. 
    with response.gather(input="speech", action='/handle-input', method='POST', timeout=5) as gather:
        gather.say(message, voice='Polly.Matthew')
        
    no_response_Msg = [
    "Oops, my circuits must've blinked. Can you repeat that?",
    "Wait, did I space out? My bad! Hit me again with that."]
    response.say(random.choice(no_response_Msg), voice='Polly.Joanna')
    return str(response)
  
call_responses = {}
@app.route("/handle-input", methods=['POST'])
def handle_input():

    user_speech = request.values.get('SpeechResult', '').lower()

    # Log the user's speech
    logger.info(f"User said: {user_speech}")

    #Handle nothing in DB error
    caller_name = None
    caller_phone_number = session.get('caller_phone_number', None)
    voice_preference = None
    email = None

    if "my name is" in user_speech:
        caller_name = user_speech.split("my name is")[-1].strip()

    if "my voice preference is" in user_speech:
        voice_preference = user_speech.split("my voice preference is")[-1].strip()

    if "my email is" in user_speech:
        email = user_speech.split("my email is")[-1].strip()

    #if caller_name:
    #    save_caller(caller_name, caller_phone_number, voice_preference, email)

    response = VoiceResponse()


    if "appointment" in user_speech:
        return handle_appointment()
        
    
    if "what's my email address" in user_speech:
        caller_data = get_caller(caller_phone_number)
        if caller_data and caller_data[4]:
            response_text = f"Your email address is {caller_data[4]}."
        else:
            response_text = "Sorry, I couldn't find your email address in our database."
        response.say(response_text, voice='Polly.Joanna')
        return str(response)
        
    # Immediate agent connection check
    if ("agent" in user_speech or 
    "human" in user_speech or 
    "representative" in user_speech or 
    "customer service" in user_speech or 
    "talk to someone" in user_speech or 
    "operator" in user_speech or 
    "real person" in user_speech):
    # redirect to a human agent
        response_text = "Hold on, I am connecting you to a real person."
        response.say(response_text, voice='Polly.Joanna')
        response.dial('+18771231234')
        return str(response)
 
    gpt_instructions = (
    "You are MY_COMPANY_NAME digital sales assistant. MY_COMPANY_NAME specializes in _______ services. "
    "Contacting them is possible via phone at 123-456-7890 or through their dedicated email addresses. "
    "For sales inquiries, reach out to sales@MY_COMPANY_NAME.com and for support, it's support@MY_COMPANY_NAME.com. "
    "To enhance their service, MY_COMPANY_NAME employs support tools like Voice over ip and IVR. "
    "If a user wishes to converse with a human, ensure you facilitate a connection to a live agent. "
    "When answering questions or handling requests, always provide concise, relevant information related to MY_COMPANY_NAME. " 
    "- Basic VoIP for Small Businesses at $24.99/month:"
    "- Premium VoIP for Growing Businesses at $34.99/month: "
    "- Customized VoIP Solutions at $45.99" 
    ) 
 
  
    # Constructing the prompt for GPT-3
    usersays = "I need a brief and direct answer. Based on the provided details, how should I respond to:"
    #logger.info(f"Agenda: {gpt_instructions}")
    #logger.info(f"Clearity: {usersays}")
    
    prompt_text = gpt_instructions + usersays + user_speech

    try:
        # Log the prompt being sent to GPT-3
        logger.info(f"Sending to GPT-3: {user_speech}")

        ai_response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt_text,
            max_tokens=100,
            temperature=0.2
        )
        response_text = ai_response.choices[0].text.strip()

        # Log the received response
        logger.info(f"Received from GPT-3: {response_text}")

    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        response_text = "Sorry, I had trouble processing that. Can I help with something else?"


    # ... [GPT-3 querying process] ...
    
    # Fallback mechanism
    if "connect to an agent" in response_text.lower() or session.get('retry_count', 0) >= 10:
        response.say("Hmmm, Let me connect you to an agent.", voice='Polly.Joanna')
        response.dial('+1231231234')
        return str(response)


    
    #response.say(response_text, voice='Polly.Joanna')

    session['retry_count'] = session.get('retry_count', 0) + 1

    with response.gather(input="speech", action='/handle-input', method='POST', timeout=5) as gather:
        #Chat GPT3 Response
        gather.say(response_text, voice='Polly.Matthew')
        if session['retry_count'] < 15: # User can go back and forth for 15 times.
            gather.say("Is there anything else you'd like to know?", voice='Polly.Joanna')
        else: # if error or if users excedes the ammount allowed to interacte with the agent then. 
            gather.say("I apologize for the inconvenience. Connecting you to a human agent...", voice='Polly.Joanna')
            response.dial('+1231231234')

    return str(response)

import dateparser 
from datetime import datetime, timedelta
 
call_responses = {}
 
@app.route("/handle-appointment", methods=['POST'])
def handle_appointment():
    try:
        user_speech = request.values.get('SpeechResult', '').lower()
        caller_number = request.values.get('From', 'Unknown')
        
        # Logging user input and caller number
        logger.info(f"Received user input for appointment: {user_speech}")
        logger.info(f"Received appointment request from: {caller_number}")

        # Fetch the caller's data associated with the number
        caller_data = get_caller(caller_number)

        caller = get_caller("+17187174431")
        print(caller)

        if caller_data:

            caller_id, caller_name, caller_phone, voice_preference, email = caller_data
            logger.info(f"Found existing caller data in DB for {caller_number}:")
            columns = ["ID", "Name", "Phone", "Voice Preference", "Email"]
            
            for column_name, value in zip(columns, caller_data):
                if value:  # Only log if the value is not None or not empty
                    logger.info(f"{column_name}: {value}")

                # Extracting the name for further processing
                _, caller_name, _, _, _ = caller_data

            #logger.info(f"Found existing caller data in DB for {caller_number}:")
            #logger.info(f"ID: {caller_id}")
            #logger.info(f"Name: {caller_name}")
            #logger.info(f"Phone: {caller_phone}")
            #logger.info(f"Voice Preference: {voice_preference}")
            #logger.info(f"Email: {email}")
            #logger.info(f"Found existing caller data in DB for {caller_number}: Name={caller_data[1]}, Voice Preference={caller_data[3]}, Email={caller_data[4]}")
            #caller_name = caller_data[1]
        else:
            logger.info(f"No data found in DB for caller: {caller_number}")
            caller_name = None
            
  

        response = VoiceResponse()

        # Debug: Log the current step for diagnosis
        logger.debug("Checking caller name...")
        
        # If there's no caller_name, prompt for it.
        if not caller_name or caller_name.isspace():
            logger.debug("Prompting for caller's name because the caller is unknown or name not found...")
            prompt_for_name(response)
        elif "appointment" in user_speech:
            logger.debug("Handling appointment request...")
            handle_appointment_request(response)
        else:
            logger.debug("Parsing provided date...")
            parsed_date = dateparser.parse(user_speech)
            if not parsed_date or parsed_date <= datetime.utcnow():
                logger.warning(f"Invalid date/time received: {parsed_date}")
                handle_invalid_datetime(response, parsed_date)
            else:
                logger.debug(f"Setting appointment for parsed date: {parsed_date}")
                set_appointment(response, parsed_date)

        return str(response)
 
    except Exception as e:
        logger.error(f"Error occurred in handle_appointment: {e}")
        raise e  # Re-raise the exception for the caller to handle or for further diagnosis

def get_caller_name(phone_number, response): 
    return None

def get_caller_name(phone_number):
    # WLC DB Get Name Attached Phone number
    # Logic to fetch the caller's name associated with the phone number from the database
    # If you have a database or system for storing associated names:
    # return fetch_name_from_database(phone_number)
    # Otherwise, return None if there's no associated name:
    return None
    
    
def prompt_for_name(response):
    """Prompt user for their name."""
    logger.info("Prompting the caller for their name...")
    response_text = "Great! What's your name?"
    with response.gather(input="speech", action='/store-name', method='POST', timeout=7) as gather:
        gather.say(response_text, voice='Polly.Joanna')
    logger.info("Awaiting user's speech input for their name.")
    return None
 
 

def handle_appointment_request(response):
    """Handle appointment request."""
    logger.debug("Handling appointment request by asking for a date and time...")
    with response.gather(input="speech", action='/handle-name', method='POST', timeout=7) as gather:
        gather.say("Please provide the date and time for the appointment.", voice='Polly.Joanna')
    logger.info("Awaiting user's speech input for appointment details.")


def handle_invalid_datetime(response, parsed_date):
    """Handle invalid datetime provided by the user."""
    logger.warning(f"Failed to parse date/time or provided date/time is in the past: {parsed_date}")
    response.say("I couldn't understand the date and time you provided. Please specify the date and time more clearly.", voice='Polly.Joanna')
    with response.gather(input="speech", action='/handle-appointment', method='POST', timeout=7) as gather:
        gather.say("Please provide the date and time for the appointment again.", voice='Polly.Joanna')
    logger.debug("Asking the user again for a valid appointment time.")


def set_appointment(response, start_time):
    """Attempt to set the appointment and send confirmation."""
    end_time = start_time + timedelta(hours=1)
    logger.info(f"Attempting to set appointment from {start_time} to {end_time}")
    try:
        success, msg = create_appointment("User Appointment", start_time, end_time)
        if success:
            logger.debug("Appointment set successfully. Sending confirmation email...")
            send_email("Appointment Confirmation", msg, 
                       current_app.config['TO_EMAIL'], 
                       current_app.config['SMTP_SERVER'],
                       current_app.config['SMTP_PORT'],
                       current_app.config['SMTP_USER'],
                       current_app.config['SMTP_PASSWORD'])
            response.say("Your appointment has been set and a confirmation email has been sent.", voice='Polly.Joanna')
            logger.info("Appointment confirmation email sent.")
        else:
            logger.error(f"Failed to set appointment: {msg}")
            response.say(msg, voice='Polly.Joanna')
    except Exception as e:
        logger.error(f"Error while setting the appointment or sending an email: {e}")
        response.say("Sorry, something went wrong. Please try again later.", voice='Polly.Joanna')


        
        

def handle_appointment_reason():
    appointment_reason = request.values.get('SpeechResult')
    caller_number = request.values.get('From', 'Unknown')
    
    # Store the appointment reason for this call
    if caller_number in call_responses:
        call_responses[caller_number]['reason'] = appointment_reason

    response_text = "Got it. Please provide the date and time for the appointment."
    
    with response.gather(input="speech", action='/handle-appointment', method='POST', timeout=7) as gather:
        gather.say(response_text, voice='Polly.Joanna')
    return str(response)


def save_to_db(data):
    # Your logic to save the provided data to the database
    message = f"{caller_name}, i am saved your phone number as {phone_number}!"
    pass
    
#def get_caller(phone_number):
#    # Logic to fetch the caller's details from the database
#    #message = f"Hello, {caller_name}! i have your number as {phone_number}, Is that correct?"
#    message = f"Hello,   i have your number as , Is that correct?"
#    pass
#    
# Assuming you have a global dictionary to temporarily store responses:
#call_responses = {}

# Define the create_appointment and send_email functions if they don't exist elsewhere in your codebase.
def create_appointment(title, start_time, end_time):
    # Placeholder function: implement the logic to create an appointment.
    return True, "Appointment created successfully"  # Example return

def send_email(subject, message, to_email, smtp_server, smtp_port, smtp_user, smtp_password):
    # Placeholder function: implement the logic to send an email.
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)
