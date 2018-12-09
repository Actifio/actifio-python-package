'''
Instantiate an Actifio object to perform operations on an Actifio appliance.

'''

import urllib3
import sys
import json
from functools import wraps

if sys.version [:3] == "2.7":
  import actexceptions
elif sys.version[0] == "3":
  import Actifio.actexceptions

# Import urlencode for the correct version
if sys.version [:3] == "2.7":
  from urllib import quote_plus as urlencode_str
  from urllib import urlencode as urlencode
elif sys.version[0] == "3":
  # NOTE: Not sure which version supports this. Working with 3.5, so limiting support to 3.5+, 
  # this is a temporary measure.
  if int(sys.version[2]) > 4: 
    from urllib.parse import quote_plus as urlencode_str
    from urllib.parse import urlencode as urlencode

# We do support self signed certs... and need to suppress unwanted chatter
urllib3.disable_warnings() 

__all__ = ['Actifio']

class ActEnforce():
  @classmethod
  def needs_token(cls,act_func):
    @wraps(act_func)
    def decorated(cls, *args, **kwargs):
      if Actifio._sessionid[cls.appliance] == '':
        try:
          print("session is empty, trying to create the session")
          Actifio._create_session(cls)
        except:
          raise
      print("Session seems to be good")
      try:
        result = act_func(cls,*args, **kwargs)
      except:
        print(act_func.__name__ + "failed")
        try:
          if not Actifio._validate_token(cls):
            try:
              Actifio._create_session(cls)
              print("created the session")
            except:
              print(" second create_session excemption")
              raise
            try:
              result = act_func(cls,*args, **kwargs)
            except:
              print(act_func.__name__ + "failed")
              raise
            else:
              return result
          else:
            raise
        except:
          print("validate token failed..")
          raise
      else:
        return result
    return decorated


class Actifio:
  #
  _sessionid = {}
  
  def __init__ (self, appliance, username, password, vendorkey, cert_validation=False):
    # functools need a __name__ for the wraps
    self.__name__ = "Actifio"
    # compose the URI for the API
    self._apiBase = "/actifio/api"
    self.appliance = appliance
    Actifio._sessionid.update( { appliance: '' } )
    # compose the login params
    self._loginParams = "/login?name=" + username 
    self._loginParams += "&password=" + password
    self._loginParams += "&vendorkey=" + vendorkey

    self._loginURI = self._apiBase + self._loginParams
    self._infoURI = self._apiBase + "/info/"
    self._taskURI = self._apiBase + "/task/"
    self._sargURI = self._apiBase + "/report/"

    # create the https poolmanager
    cert_str = 'CERT_REQUIRED' if cert_validation else 'CERT_NONE'

    self._httppool = urllib3.HTTPSConnectionPool (host=appliance, port=443, cert_reqs=cert_str)

  @staticmethod
  def _validate_token (self):
    """
    Validate the exisiting _sessionid token. Return True if the token is valid.
    """
    
    if Actifio._sessionid[self.appliance] == '' :
      return False
    try:
      resp = self._httppool.request (
        'GET',
        self._infoURI + 'lsversion?sessionid=' + Actifio._sessionid[self.appliance]
      )
    except Exception:
      raise ActConnectError("Unable to reach the appliance: check the IP address / hostname")
    else:
      if resp.status != 200:
        return False
      else:
        return True


  @staticmethod
  def _create_session (self):
    """
    Create a new session taken 
    """
    try:
      login = self._httppool.request (
        'GET',
        self._loginURI
      )
    except Exception as e:
      raise ActConnectError("Unable to reach the appliance: check the IP address / hostname")
    else:
      try:    
        response = json.loads(login.data)
      except:
        raise ActLoginError("This does not seem to be a Actifio Sky/CDS appliance")
      if login.status == 200:
        try:
          Actifio._sessionid[self.appliance] = response['sessionid']
        except:
          raise ActLoginError(response['errormessage'])
      else:
        raise ActLoginError("This does not seem to be a Actifio Sky/CDS appliance")



  @ActEnforce.needs_token
  def run_uds_command(self, cmdType, cmdUDS, cmdArgs):
    """
    Wrapper function to convert CLI commands to the rest API.
      cmdType: info / task 
      cmdUDS: Command to use (eg. lsuser, lshost, mkapplication... etc.)
      cmdArgs: Dictionary with arguments to the command
               For example: 
               vmdiscovery -discovercluster -host 1234 
               { 'discovercluster': None, 'host': 1234 }

               lsapplication -filtervalues "appname=mydb&hostname=myhost"
               { 'filtervalues': { 'appname': 'mydb', 'hostname': 'myhost' } }

               lshost 123
               { 'argument': 123 }

               RESTfulAPI_*.pdf would be good referecne point for the __SIMILARITY__ and 
               __PATTERN__.
    """

    _URI = self._infoURI if cmdType == "info" else self._taskURI

    # append the command to URI
    _URI += cmdUDS + '?'

    # append the argument
    for key in cmdArgs:
      if type(cmdArgs[key]) == dict:
        # Actifio API expects this to be urlencoded
        _URI += key + '=' + urlencode_str(urlencode(cmdArgs[key])) + '&' 
      elif cmdArgs[key] == None:
        _URI += key + '&'
      else:
        _URI += key + '=' + cmdArgs[key] + '&'
        
    _URI += 'sessionid=' + Actifio._sessionid[self.appliance]
  
    try:
      udsout = self._httppool.request (
        'GET' if cmdType == 'info' else 'POST',
        _URI
      )
    except Exception as e:
      print(type(e))
      raise ActExceptionConnect
    else:
      response = json.loads(udsout.data)
      if udsout.status != 200:
        self._lastout = ''
        raise ActAPIError(response['errormessage'])
      else:
        self._lastout = response
        return self._lastout


  @ActEnforce.needs_token
  def run_sarg_command(self, cmdSARG, cmdArgs):
    """
    Wrapper function to convert CLI commands to the rest API. 
      cmdSARG: Command to use (eg. reportsnaps, reportapps... etc.)
      cmdArgs: Dictionary with arguments to the command
               For example: 
               reportapps -a 1234 -x
               { 'a': 1234, 'x': None }
    """

    _URI = self._sargURI

    # append the command to URI
    _URI += cmdSARG + '?'

    # append the argument
    for key in cmdArgs:
      if type(cmdArgs[key]) == dict:
        # Actifio API expects this to be urlencoded
        _URI += key + '=' + urlencode_str(urlencode(cmdArgs[key])) + '&' 
      elif cmdArgs[key] == None:
        _URI += key + '&'      
      else:
        _URI += key + '=' + cmdArgs[key] + '&'
        
    _URI += 'sessionid=' + Actifio._sessionid[self.appliance]

    try:
      sargout = self._httppool.request (
        'GET',
        _URI
      )
    except urllib3.exceptions.NewConnectionError:
      raise ActConnectError("Unable to make connection to the appliance")
    else:
      response = json.loads(sargout.data)
      if sargout.status != 200:
        self._lastout = ''
        raise ActAPIError(response['errormessage'])
      else:
        self._lastout = response
        return self._lastout

  
  def create_or_replace_iscsi_host(self, name, ipaddress, host_type='generic', dsik_pref='BLOCK', detect_as_vm=False):
    #check whether the host entry exists
    try:
      lshost = self.run_uds_command('info', 'lshost',{ 'filtervalue': { 'hostname': name}})
    except:
      raise
    else:
      if 1 > len(lshost['result']) > 0:
        #found the host:
        host_id = lshost['result'][0]['id']
      else:
        self.run_uds_command('task','chhost',{ 'hostname': name})

