#!/usr/bin/env python3 

from flask import Flask
from Actifio import Actifio
from chartjs import ChartJS, ChartDatalet, ChartDataset
#from mdl_analyser import MDL

import getpass
import base64
import os
import json
import argparse
from datetime import datetime

cli_args = argparse.ArgumentParser(description="CLI Arguments")

cli_args.add_argument('-a', '--appliance', type=str, nargs=1, help="Appliance IP", required=False)
cli_args.add_argument('-u', '--user', type=str, nargs=1, help="Actifio Username", required=False)
cli_args.add_argument('-p', '--password', type=str, nargs=1, help="Actifio password", required=False)

arguments = cli_args.parse_args()

print (arguments)

while 1:

  try:
    if arguments.appliance == None:
      APPLIANCE = input('Appliance: ')
    else:
      APPLIANCE = arguments.appliance[0]
  except:
    pass


  try:
    if arguments.user == None:
      USERNAME = input("Username: ")
    else:
      USERNAME = arguments.user[0]
  except:
    pass

  try:
    if arguments.password == None:
      PASSWORD = getpass.getpass(prompt="Password: ")
    else:
      PASSWORD = arguments.password[0]
  except:
    pass

  act = Actifio(APPLIANCE, USERNAME, PASSWORD, verbose=True)

  try:
    mdldata = act.run_uds_command("info","lsmdlstat",{ 'filtervalue': {"stattime": "> 2020-03-15"}})  
  except Exception as e:
    print ("Something didn't go as planned: " + str(e))
  else:
    break

mdl_analyser = Flask("mdl_analyser")
mdl_analyser.port = 5100

@mdl_analyser.route("/")
def home ():
  try:
    with open("chart.html") as f:
      return f.read()
  except:
    pass

@mdl_analyser.route("/start")
def analyser_start ():
  return "This is from JQ/AJAX"

@mdl_analyser.route("/applist")
def list_applications ():
  appnamelist = {}
  for m in mdldata['result']: 
    if not m['appname'] in appnamelist.keys(): 
      appnamelist[m['appname']] = m['appid'] 

  return json.dumps(appnamelist)

@mdl_analyser.route("/chartdata")
def gen_chart_for_all ():
  chart = ChartJS("MDL Analyser", stacked=True)
  chart.set_legend()  
  for m in mdldata['result']: 
    if not m['appid'] == '0': 
      stat_day = datetime.strptime(m['stattime'][0:10], "%Y-%m-%d")
      chart.add_data(m['appname'], stat_day, int(int(m['manageddata'])/1024/1024/1024))

  return chart.render_json_config()


if __name__ == "__main__":
  mdl_analyser.run(port=5100)

