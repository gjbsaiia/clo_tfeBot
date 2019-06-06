#!python3

# native python libs
import os
import sys
import json
import requests
import base64
import time
from email.mime.text import MIMEText
import pickle
# google libs
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Convention is as follows:
#   "FirstName": [["AWS Workspace", "Azure Workspace"], "user_email"]
branchDic = {
    "Griffin": [["ws-eogvTqraZV4a2Pzt", "ws-Mi7GaLeksgfvcXZW"], "griffin_j_saiia@progressive.com"],
}

provider = ["AWS", "Azure"]

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
didRun = -1

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
def getState(workspace, i):
    global mytoken, headers, base_url, didRun
    outputs = []
    url = base_url+workspace+"/runs"
    auth = {'Authorization':"Bearer "+mytoken}
    headers.update(auth)
    response = requests.request("GET", url, headers=headers)
    all = json.load(response)
    data = all["data"]
    for key in run:
        if(key == "id"):
            outputs.append(["run",run[key]])
        if(key == "attributes"):
            attributes = run[key]
            for key in attributes:
                if(key == "status"):
                    if(attributes[key] == "errored"):
                        didRun = -1
                    else:
                        didRun = i
                    outputs.append(["status",attributes[key]])
        if(key == "links"):
            links = run[key]
            for key in links:
                outputs.append(["link to run",url+links[key]])
    return outputs


def composeMsg(name, outputs, path):
    global didRun
    lines = []
    msg = ""
    with open(path) as template:
        lines = template.readlines()
        template.close()
    i = 0
    for line in lines:
        if(i == 1):
            msg+=name+",\n\n"
        if(i == 2):
            msg+=(branchDic[name][0][didRun]+"\n")
            if(didRun > -1):
                msg+="\n"
        if(i == 3):
            for each in outputs:
                msg+="    "+each[0]+": "+each[1]+"\n"
            msg+="\n"
        msg += line
        i += 1
    return msg

def sendMail(name, email, outputs, service):
    global didRun, success, fail, provider, branchDic
    body = ""
    path = ""
    if(didRun > -1):
        path = success
    else:
        path = fail
    body = composeMsg(name, outputs, path)
    message = MIMEText(body)
    message['to']=email
    message['from']="tfe.service.bot@gmail.com"
    if(didRun > -1):
        message['subject']="TFE RUN ALERT: "+branchDic[name][0][didRun]+" on "+provider[didRun]
    else:
        message['subject']="TFE RUN ALERT: Job Failed"
    b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
    b64_string = b64_bytes.decode()
    body = {'raw': b64_string}
    try:
        sendMsg = service.users().messages().send(userId="me", body=body).execute()
        print("Message Id: "+sendMsg['id'])
    except:
        print("Send failed. An Error occurred.")

def readyMailCall(name, outputs):
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    email = branchDic[name][1]
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

def main():
    global didRun, branchDic
    outputs = []
    name = ""
    #onStart()
    #while(True):
    while(didRun < 0):
        for key in branchDic:
            i = 0
            name = key
            spaces = branchDic[key][0]
            for each in spaces:
                outputs = getState(each, i)
                readyMailCall(name, outputs)
                time.sleep(5)
                i+= 1
    time.sleep(5)

if __name__ == '__main__':
    main()
