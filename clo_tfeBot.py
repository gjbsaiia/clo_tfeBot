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
from datetime import datetime
import clo-pyghe
from clo-pytfe import pytfe

#import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport,requests import Request

branchDic = {
    "feature-griffin_repo": ["griffin", "griffin_j_saiia@progressive.com"],
    "feature-robbie_repo": ["robbie", "robbie_j_barnes@progressive.com"],
    "feature-dhanush_repo": ["dhanush", "dhanush_venkatesh@progressive.com"]
}

# branch-to-workspace dictionary
branch_spaces = {}
# creds
mytoken = os.getenv('ATLAS_TOKEN') # check for this on local machine
# tfe client obj
client = pytfe.TfeClient(atlas_token=mytoken, org="ets")
#msg paths
success = "configuration_output.txt"
fail = "configuration_failure.txt"
#flag
didRun = false

# pull down all active workspaces
def onStart():
    active_workspaces = client.list_workspaces()
    getWorkspaces(active_workspaces)

# pull out all workspaces with our names (works for interns)
def getWorkspaces(workspaces):
    for each in workspaces:
        for key in branchDic:
            if each.contains(branchDic[key][0]):
                try:
                    branch_spaces.add(branchDic[key][0]:[each])
                except KeyError:
                    branch_spaces.update(branchDic[key][0], branch_spaces[branchDic[key][0].add(each)])

# grab .json state file, ensure it's up to date
def getState(name):
    ct = datetime.ctime # needs format matching .json --> allow +/- 3s?

    # need to check for job failure,, test 'client.show_workspace_current_run(workspace_name=branch_spaces[key])'

    #get all runs in a given workspace
        #GET /workspaces/:workspace_id/runs

    state_obj = client.get_raw_state(workspace_name=branch_spaces[key])
    data = json.load(state_obj)

def composeMsg(name, outputs, path):
    lines = []
    msg = ""
    with open(path) as template:
        lines = template.readlines()
        entries.close()
    i = 0
    for line in lines:
        if(i == 1):
            msg+=key+"\n"
        if(i == 2):
            msg+=branch_spaces[key]+"\n"
        if(i == 3):
            for each in outputs:
                msg+=each[0]+": "+each[1]+"\n"
        msg += line
        i++
    return msg

def sendMail(name, email, outputs):
    body = ""
    path = ""
    if(didRun):
        path = "configuration_output.txt"
    else:
        path = "configuration_failure.txt"
    body = composeMsg(name, outputs, path)
    message = MIMEText(body)
    message['to']=email
    message['from']=service_address
    message['subject']="TFE RUN ALERT: "+branch_spaces[name]
    encoded = base.urlsafe_b64encode(message.as_string())
    try:
        sendMsg = (service.users().messages().send(userId=user_id, body=encoded).execute())
        print("Message Id: "+sendMsg['id'])
    except errors.HttpError, error:
        print("Send failed. An Error occurred: "+error)