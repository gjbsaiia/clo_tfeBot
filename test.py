import pickle
import base64
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText

didRun = False

branch_spaces = {
    "griffin": "feature-griffin_repo"
}

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    name = "griffin"
    email = "griffin_j_saiia@progressive.com"
    outputs = []#["this", "is"], ["a", "test"], ["!", "\\_['_']_/"]]
    sendMail(name, email, outputs, service)

def composeMsg(name, outputs, path):
    global didRun
    lines = []
    msg = ""
    key = name.lower()
    with open(path) as template:
        lines = template.readlines()
        template.close()
    i = 0
    for line in lines:
        if(i == 1):
            msg+=key+",\n\n"
        if(i == 2):
            msg+=branch_spaces[key]+"\n"
            if(didRun):
                msg+="\n"
        if(i == 3):
            for each in outputs:
                msg+="    "+each[0]+": "+each[1]+"\n"
            msg+="\n"
        msg += line
        i += 1
    return msg

def sendMail(name, email, outputs, service):
    global didRun
    #didRun = True
    body = ""
    path = ""
    if(didRun):
        path = "configuration_output.txt"
    else:
        path = "configuration_failure.txt"
    body = composeMsg(name, outputs, path)
    message = MIMEText(body)
    message['to']=email
    message['from']="tfe.service.bot@gmail.com"
    message['subject']="TFE RUN ALERT: "+branch_spaces[name]
    b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
    b64_string = b64_bytes.decode()
    body = {'raw': b64_string}
    try:
        sendMsg = service.users().messages().send(userId="me", body=body).execute()
        print("Message Id: "+sendMsg['id'])
    except:
        print("Send failed. An Error occurred.")

if __name__ == '__main__':
    main()
