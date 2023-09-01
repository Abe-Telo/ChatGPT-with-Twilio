import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = 'your_flask_secret_key'
    SESSION_TYPE = 'filesystem'
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = os.getenv('SMTP_PORT')
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    TO_EMAIL = os.getenv('TO_EMAIL')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    
class gpt3Msg:
    Welcome_Msg = ("Hello! Welcome to My Company Name. Quick note: I'm the new digital kid on the block."
               "Think of me as the chatbot version of baby Yoda, but powered by some GPT wizardry. We can chat about anything, "
               "set up appointments, and even exchange a joke or two. And hey, if you ever get nostalgic for human interaction, "
               "just say the word and I'll connect you to an actual human. So, what fun task can I assist with today?")
               
    no_response_Msg = ["Oops, my circuits must've blinked. Can you repeat that?",
                       "Wait, did I space out? My bad! Hit me again with that."]
                
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
