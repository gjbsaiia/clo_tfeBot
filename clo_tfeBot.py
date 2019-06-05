#!python


# Resources::
# https://www.terraform.io/docs/enterprise/api/run.html
# https://githubprod.prci.com/progressive/clo-pyghe/blob/develop/clo_pyghe/pyghe.py
# https://githubprod.prci.com/progressive/clo-pytfe/blob/master/clo_pytfe/pytfe.py
# https://githubprod.prci.com/progressive/clo-slfsrvc-tools/blob/feature-ptfe/ptfe/plan_apply_logs/tfe_apply_logs.py

import os
import sys
import json
import requests
import base64
from datetime import datetime
from email.mime.text import MIMEText
import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

branchDic = {
    "Griffin": [["ws-eogvTqraZV4a2Pzt", "ws-Mi7GaLeksgfvcXZW"], "griffin_j_saiia@progressive.com"],
}

# base url
base_url = "https://clo-tfe-prod.prci.com/api/v2/workspaces/"

# headers
headers = {
    'Content-Type': "application/vnd.api+json",
    'data': "@payload.json",
    'Cache-Control': "no-cache",
    'Postman-Token': "c6496ff7-9665-4de7-bdec-243dd23321d1"
}

# creds
mytoken = ""
#msg paths
success = "configuration_output.txt"
fail = "configuration_failure.txt"
#flag
didRun = false

# pull down all active workspaces
def onStart():
    global mytoken
    get_tfe_token()

# pulls token out of .txt file in root directory
def get_tfe_token():
    global mytoken
    with open("tfe_token.txt") as token_txt:
        lines = token_text.readlines()
        mytoken = lines[0]
        token_txt.close()

# grab .json state file, ensure it's up to date
def getState(workspace):
    global mytoken, headers
    url = base_url+workspace+"/runs"
    auth = {'Authorization':"Bearer "+mytoken}
    headers.update(auth)
    response = requests.request("GET", url, headers=headers)
    data = json.load(response)


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

def sendMail(name, email, outputs):
    global didRun, success, fail
    body = ""
    path = ""
    if(didRun):
        path = success
    else:
        path = fail
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

def readyMailCall():
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
    sendMail(name, email, outputs, service)

if __name__ == '__main__':
    main()
