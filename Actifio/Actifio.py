'''
Instantiate an Actifio object to perform operations on an Actifio appliance.

'''

import urllib3
import sys
import json
from functools import wraps
from ActHosts import ActHosts

# import custom exceptions 
if sys.version [:3] == "2.7":
  from actexceptions import *
elif sys.version[0] == "3":
  from Actifio.actexceptions import *

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
          Actifio._create_session(cls)
        except:
          raise
      try:
        result = act_func(cls,*args, **kwargs)
      except:
        try:
          if not Actifio._validate_token(cls):
            try:
              Actifio._create_session(cls)
            except:
              raise
            try:
              result = act_func(cls,*args, **kwargs)
            except:
              # print(act_func.__name__ + "failed")
              raise
            else:
              return result
          else:
            raise
        except:
          raise
      else:
        return result
    return decorated


class Actifio:
  #
  _sessionid = {}
  
  def __init__ (self, appliance, username, password, vendorkey="python-wrapper", cert_validation=False):
    # functools need a __name__ for the wraps
    self.__name__ = "Actifio"
    # compose the URI for the API
    self._apiBase = "/actifio/api"
    self.appliance = appliance
    self.username = username
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

  def __str__(self):
    if Actifio._sessionid[self.appliance] == "":
      return "Connection not verified; Appliance: " + str(self.appliance) + "; Username: " + str(self.username)
    else:
      return "Connection verified (session id): " + str(Actifio._sessionid[self.appliance]) + "; Appliance: " + str(self.appliance) + "; Username: " + str(self.username)

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
  def run_uds_command(self, cmdType, cmdUDS, cmdArgs={}):
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
        _URI += key + '=' + urlencode_str('&'.join([ filter_key + '=' + cmdArgs[key][filter_key] for filter_key in cmdArgs[key]])) + '&'
      elif cmdArgs[key] == None:
        _URI += urlencode_str(key) + '&'
      else:
        _URI += urlencode_str(key) + '=' + urlencode_str(str(cmdArgs[key])) + '&'
        
    _URI += 'sessionid=' + Actifio._sessionid[self.appliance]
    try:
      udsout = self._httppool.request (
        'GET' if cmdType == 'info' else 'POST',
        _URI
      )  
    except Exception as e:
      print (e)
      raise ActConnectError("Failed to connect the appliance")
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
        _URI += key + '=' + urlencode_str('&'.join([ filter_key + '=' + cmdArgs[key][filter_key] for filter_key in cmdArgs[key]])) + '&'
      elif cmdArgs[key] == None:
        _URI += urlencode_str(key) + '&'
      else:
        _URI += urlencode_str(key) + '=' + urlencode_str(str(cmdArgs[key])) + '&'
        
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

  
  def define_iscsi_host(self, hostname, ipaddress, host_type='geenric', dsik_pref='BLOCK', detect_as_vm=False):
    #check whether the host entry exists
    try:
      lshost = self.run_uds_command('info', 'lshost',{ 'filtervalue': { 'hostname': hostname }})
    except:
      raise
    else:
      if len(lshost['result']) > 0:
        #found the host:
        host = lshost['result']
      else:
        self.run_uds_command('task','chhost',{ 'hostname': name})

  def clone_database(self, source_hostname, source_appname, target_hostname, **kwargs):
    '''
    This method creates a virtual clone of Oracle or SQL server database.
      source_hostname: Hostname of the source host where the database was captured from
      source_appname: source application name, or the database name
      target_hostname: target host where the virtual clone need to be created on

      Oracle Related Parameters:
        oracle_home (required): ORACLE_HOME
        oracle_db_name (required): SID of the target clone
        oracle_tns_admin (optional): TNS admin path
        oracle_db_mem (optional): Total Memory Target for the database
        oracle_sga_pct (optional): Memory Percentage to allocate for SGA
        oracle_redo_size (optional): Redo Log size in MB, defaults to 500
        oracle_shared_pool (optional): Oracle Shared Pool size
        oracle_db_cache_size (optional): Oracle DB Cache size
        oracle_recover_dest_size (optional): Oracle Parameter db_recover_dest_size. Defaults to 5000
        oracle_diagnostic_dest (optional): Oracle Diagnostic Destination
        oracle_nprocs (optional): Num of Max processes
        oracle_open_cursors (optional): Number of open_cursors. defaults to 1000 
        oracle_char_set (optional): Characterset. Defaults to 'AL32UTF8'
        oracle_tns_ip (optional): TNS IP Address
        oracle_tns_port (optional): TNS Port
        oracle_tns_domain (optional): TNS Domain
        oracle_no_nid (optional): Do not change the DBID of the new clone. Will maintain same DBID as the source. Defaults to FALSE
        oracle_no_tns_update (optional): Do not update TNS records. Defaults to FALSE
        oracle_restore_recov (optional): Recover the oracle database. Defaults to TRUE
        oracle_no_rac (optional): Treat as Oracle RAC. Defaults to TRUE

      SQLServer Related
        sql_instance_name (required): Target SQL Server instance name
        sql_recover_userlogins (optional): Recover user logins of the database. Defaults to FALSE
        sql_username (optional): Username for database provisioning
        sql_password (optional): Password for the specified user 
        
      SQLServer DB Application
        sql_db_name (reuired): Database name at the target instance. (Only required if the source application is database or single database mount from instance.) 

      SQLServer Instance 
        sql_source_dbnames (required): Source database names if the source application is SQL instance. Use ',' as delimiter for multiple databases. (Only required if the source application is SQL server instance.) 
        sql_cg_name (required): Consistency group name. (Only required if the source application is SQL Server instance and mount multiple databases at a time.)
        sql_dbname_prefix (optional): Prefix of database name for multiple database mount
        sql_dbname_suffix (optional): Suffix of database name for multiple database mount

    '''

    application = self.run_uds_command("info","lsapplication", {"filtervalue": { "appname": source_appname, "hostname": source_hostname, "apptype!": "VMBackup" }})
    pass
