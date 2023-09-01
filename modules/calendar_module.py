#calender_module.py
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """
    Authenticate and return the Google Calendar service.
    """
    creds = None
    logging.debug("Attempting to load credentials from token.pkl")

    # Try loading credentials from token.pkl file
    if os.path.exists('token.pkl'):
        with open('token.pkl', 'rb') as token:
            creds = pickle.load(token)
            logging.debug("Loaded credentials from token.pkl successfully.")

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logging.debug("Refreshing expired credentials.")
            creds.refresh(Request())
        else:
            logging.debug("Getting new credentials via offline OAuth flow.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_console()  # This is the offline authentication

            # Save the credentials for future runs
            with open('token.pkl', 'wb') as token:
                pickle.dump(creds, token)
            logging.debug("New credentials obtained and saved to token.pkl")

    logging.debug("Building Google Calendar service.")
    service = build('calendar', 'v3', credentials=creds)
    return service


 


def add_to_calendar(event_details):
    """
    Add an event to the primary Google Calendar.
    """
    service = get_calendar_service()
    logging.info(f"Attempting to add event: {event_details['summary']}")
    event = service.events().insert(calendarId='primary', body=event_details).execute()
    logging.debug(f"Raw API response: {event}")
    return event

if __name__ == '__main__':
    # Test the Google Calendar integration
    start_time = datetime.datetime.utcnow()
    end_time = start_time + datetime.timedelta(hours=1)

    # Testing add_to_calendar directly
    sample_event_details = {
    'summary': f"Appointment - {reason}",
    'description': f"Type: {appointment_type}. Phone Number: {caller_number}",
    'start': {
        'dateTime': start_time.isoformat() + 'Z',
        'timeZone': timeZone,
    },
    'end': {
        'dateTime': end_time.isoformat() + 'Z',
        'timeZone': timeZone,
    },
    }
    
    
    

    event = add_to_calendar(sample_event_details)
    if event and event.get('htmlLink'):
        print(f"Event created (add_to_calendar): {event.get('htmlLink')}")
        logging.info(f"Test event created (add_to_calendar): {event.get('htmlLink')}")
    else:
        logging.error("Failed to create the test event.")

    # Testing create_appointment function
    success, message = create_appointment('Test Appointment using create_appointment', start_time, end_time, 'Testing the Google Calendar integration via create_appointment.')

    if success:
        print(message)
        logging.info(message)
    else:
        logging.error(f"Failed to create the test event: {message}")


def create_appointment(summary, start_time, end_time, description='', timeZone='UTC'):
    """
    Create a Google Calendar appointment based on the provided details.
    Params:
    - summary (str): Title of the appointment.
    - start_time (datetime): Start time of the appointment.
    - end_time (datetime): End time of the appointment.
    - description (str, optional): Description of the appointment.
    - timeZone (str, optional): Time zone of the appointment. Default is 'UTC'.
    
    Returns:
    - tuple: (success (bool), message (str))
    """
    logging.debug(f"Started Module create_appointment")

    # Prepare the event details dictionary
    event_details = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat() + 'Z',
            'timeZone': timeZone,
        },
        'end': {
            'dateTime': end_time.isoformat() + 'Z',
            'timeZone': timeZone,
        },
    }

    try:
        logging.debug(f"Attempting to create event with details: {event_details}")
        event = add_to_calendar(event_details)
        logging.debug(f"Event created successfully with link: {event.get('htmlLink')}")
        return (True, f"Event created: {event.get('htmlLink')}")
    except Exception as e:
        logging.error(f"Error creating event: {e}")
        return (False, str(e))


if __name__ == '__main__':
    # Test the Google Calendar integration
    start_time = datetime.datetime.utcnow()
    end_time = start_time + datetime.timedelta(hours=1)
    
    success, message = create_appointment('Test Appointment', start_time, end_time, 'Testing the Google Calendar integration.')
    
    if success:
        print(message)
        logging.info(message)
    else:
        logging.error(f"Failed to create the test event: {message}")
