#    Access to an SMTP server (for this example, I'll be using Gmail's SMTP server).
#    Installed necessary package: pip install smtplib.

#    Security: Storing your email and password directly in a script (as in the above test example) isn't a secure practice. In production, consider storing credentials securely, for instance, using environment variables or a secure vault.
#    Gmail Restrictions: If you're using Gmail's SMTP for testing, remember that Google will block sign-ins from the app trying to use this script, deeming it less secure. To test using Gmail, you must allow "less secure apps" in your Google account settings. This is not recommended for a production environment due to security reasons.

#If you're planning to use this in a production environment, consider using transactional email services like SendGrid, Mailgun, or AWS SES that provide more robust APIs for sending emails programmatically.



import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def send_email(subject, body, to_email, smtp_server, smtp_port, smtp_user, smtp_password):
    """
    Send an email.
    
    Params:
    - subject (str): Email subject.
    - body (str): Email body content.
    - to_email (str): Recipient's email address.
    - smtp_server (str): SMTP server address.
    - smtp_port (int): SMTP server port.
    - smtp_user (str): SMTP server user (email address).
    - smtp_password (str): SMTP server user password.
    """
    # Prepare the MIMEText objects
    msg = MIMEMultipart()
    msg.attach(MIMEText(body, 'plain'))
    
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject

    try:
        # Connect to the SMTP server and send the email
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, msg.as_string())
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")


if __name__ == '__main__':
    # Testing the email function using environment variables
    SUBJECT = "Test Email from email_module.py"
    BODY = "This is a test email sent from the email_module script. If you receive this, the function works!"
    
    # Use environment variables to fetch these details
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 465))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    TO_EMAIL = os.getenv('TO_EMAIL')

    send_email(SUBJECT, BODY, TO_EMAIL, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD)
