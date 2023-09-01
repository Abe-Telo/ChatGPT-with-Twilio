""" Offline google calender authenticate
    when your authenticate google calender, you might get a 400 request. 
    Instead copy the link and past it to the command line to create your token.pk1 file"""

import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  

from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
from urllib.parse import urlparse, parse_qs
import qrcode

def authenticate_and_save_token():
    # Load client secrets and set the redirect_uri
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', ['https://www.googleapis.com/auth/calendar'], redirect_uri="http://localhost:8080/"
    )

    # Generate authorization URL
    auth_url, state = flow.authorization_url(
        prompt="consent",
        access_type="offline"
    )
    
    print("Please go to this URL:", auth_url)
    
    auth_response = input("Enter the full redirect URL: ")

    # Extract state from the response URL
    returned_state = parse_qs(urlparse(auth_response).query).get("state")

    # Check if state is present in the response URL
    if not returned_state:
        raise ValueError("No state parameter found in the URL you entered. Please ensure you're copying the full redirect URL.")

    # Check if the states match
    if returned_state[0] != state:
        raise ValueError("State mismatch. Exiting for security.")

    # Fetch the token
    flow.fetch_token(authorization_response=auth_response)
    
    # Save the credentials to a pickle file
    with open('token.pkl', 'wb') as token:
        pickle.dump(flow.credentials, token)

    print("Authentication complete and token saved to token.pkl")

if __name__ == "__main__":
    authenticate_and_save_token()
