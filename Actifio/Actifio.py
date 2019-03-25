'''
Instantiate an Actifio object to perform operations on an Actifio appliance.

'''
import sys
import json
from functools import wraps
import urllib3

# import auxialary libraries
if sys.version [:3] == "2.7":
  from actexceptions import *
  from ActSupportClasses import ActHost, ActHostCollection
  from ActSupportClasses import ActApplication, ActAppCollection
  from ActSupportClasses import ActImage, ActImageCollection
  from ActSupportClasses import ActJob, ActJobsCollection
elif sys.version[0] == "3":
  from Actifio.actexceptions import *
  from Actifio.ActSupportClasses import ActHost, ActHostCollection
  from Actifio.ActSupportClasses import ActApplication, ActAppCollection
  from Actifio.ActSupportClasses import ActImage, ActImageCollection
  from Actifio.ActSupportClasses import ActJob, ActJobsCollection

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
  def needs_token(cls, act_func):
    @wraps(act_func)
    def decorated(cls, *args, **kwargs):
      if Actifio._sessionid[cls.appliance][cls.username] == '':
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
              # print ("creating session id")
              Actifio._create_session(cls)
            except:
              raise
            try:
              result = act_func(cls, *args, **kwargs)
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

  @classmethod
  def needs_version(cls, act_func):
    @wraps(act_func)
    def decorated(cls, *args, **kwargs):
      if cls.version == 'not_known':
        version = cls.run_uds_command('info', 'lsversion', {})
        cls.version = version['result'][0]['version']
      try:
        return act_func(cls, *args, **kwargs)
      except:
        # print(act_func.__name__ + "failed")
        raise
    return decorated


class Actifio:
  """
  Actifio instance:

  Attributes:

    :appliance: IP or FQDN of the appliance
    :username: Username to login to the appliance
    :password: Password
    :cert_validation: Certificate validation for SSL connections.
                      Defaults to false.

  """
  _sessionid = {}

  def __init__(self, appliance, username, password, cert_validation=False):
    """
    Actifio instance:

    :appliance: IP or FQDN of the appliance
    :username: Username to login to the appliance
    :password: Password

    """
    # vendor key is fixed
    vendorkey = "195B-4370-2506-0A60-1F41-5829-067B-603C-6737-1244-0A11-6742-0745-4023-1A"
    # functools need a __name__ for the wraps
    self.__name__ = "Actifio"
    # compose the URI for the API
    self._apiBase = "/actifio/api"
    self.appliance = appliance
    self.username = username
    self.version = 'not_known'
    #sessionid is unique per user in an appliance
    Actifio._sessionid.update({appliance: {}})
    Actifio._sessionid[appliance].update({ username: ''})
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

    self._httppool = urllib3.HTTPSConnectionPool(host=appliance, port=443, cert_reqs=cert_str)

  def __str__(self):
    if Actifio._sessionid[self.appliance][self.username] == "":
      return "Connection not verified; Appliance: " + str(self.appliance) + "; Username: " + str(self.username)
    else:
      return "Connection verified (session id): " + str(Actifio._sessionid[self.appliance][self.username]) + "; Appliance: " + str(self.appliance) + "; Username: " + str(self.username)

  @staticmethod
  def _validate_token(self):
    """
    Validate the exisiting _sessionid token. Return True if the token is valid.
    """

    if Actifio._sessionid[self.appliance][self.username] == '':
      return False
    try:
      resp = self._httppool.request(
        'GET',
        self._infoURI + 'lsversion?sessionid=' + Actifio._sessionid[self.appliance][self.username]
      )
    except Exception:
      raise ActConnectError("Unable to reach the appliance: check the IP address / hostname")
    else:
      if resp.status != 200:
        return False
      else:
        return True

  @staticmethod
  def _create_session(self):
    """
    Create a new session taken
    """
    try:
      login = self._httppool.request(
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
          Actifio._sessionid[self.appliance][self.username] = response['sessionid']
        except:
          raise ActLoginError(response['errormessage'])
      elif login.status == 401:
        if response.get('errorcode') == 10011:
          raise ActLoginError("Invalid username or password")
        else:
          raise ActLoginError("This does not seem to be a Actifio Sky/CDS appliance")
      else:
        raise ActLoginError("This does not seem to be a Actifio Sky/CDS appliance")

  @ActEnforce.needs_version
  #@staticmethod
  def _minimum_version (self, min_version):

    comp_version = self.version.split(".")
    comp_min_version = min_version.split(".")

    for index in [0, 1, 2, 3]:
      if int(comp_version[index]) > int(comp_min_version[index]):
        return True
      if int(comp_version[index]) < int(comp_min_version[index]):
        return False
    return True

  @ActEnforce.needs_token
  def run_uds_command(self, cmdType,
    cmdUDS,
    cmdArgs={}):
    """
    Wrapper function to convert CLI commands to the rest API.

    Args:

      :cmdType: info / task
      :cmdUDS: Command to use (eg. lsuser, lshost, mkapplication... etc.)
      :cmdArgs: Dictionary with arguments to the command

    Returns:

      Returns a dictionary of API response.

    Example:

      vmdiscovery -discovercluster -host 1234

      { 'discovercluster': None, 'host': 1234 }

      lsapplication -filtervalues "appname=mydb&hostname=myhost"

      { 'filtervalues': { 'appname': 'mydb', 'hostname': 'myhost' } }

      lshost 123

      { 'argument': 123 }


    .. note:: RESTfulAPI_*.pdf would be good referecne point for the __SIMILARITY__ and __PATTERN__ of the cmdArgs.

    """

    _URI = self._infoURI if cmdType == "info" else self._taskURI

    # append the command to URI
    _URI += cmdUDS + '?'

    # provision for the non-equal opprations
    def __regex_args(key, value):
      import re
      not_equal = re.compile(r'^not\s+(.*)')
      greater_than = re.compile(r'^\>\s*(.*)')
      smaler_than = re.compile(r'^\<\s*(.*)')

      ne_match = not_equal.search(value)
      gt_match = greater_than.search(value)
      st_match = smaler_than.search(value)

      if ne_match is not None:
        return key + "!=" + ne_match.group(1)
      if st_match is not None:
        if key != "provisioningoptions":
          return key + "<" + st_match.group(1)
      if gt_match is not None:
        return key + ">" + gt_match.group(1)
      else:
        return key + "=" + value

    # append the argument
    for key in cmdArgs:
      if type(cmdArgs[key]) == dict:
        # Actifio API expects this to be urlencoded
        _URI += key + '=' + urlencode_str('&'.join([ __regex_args(filter_key, cmdArgs[key][filter_key]) for filter_key in cmdArgs[key]])) + '&'
      elif cmdArgs[key] == None:
        _URI += urlencode_str(key) + '&'
      else:
        _URI += urlencode_str(key) + '=' + urlencode_str(str(cmdArgs[key])) + '&'

    _URI += 'sessionid=' + Actifio._sessionid[self.appliance][self.username]
    try:
      udsout = self._httppool.request (
        'GET' if cmdType == 'info' else 'POST',
        _URI
      )
      # print(_URI)
    except Exception as e:
      # print (e)
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
  def run_sarg_command(self, cmdSARG, cmdArgs={}):
    """
    Wrapper function to convert CLI commands to the rest API.

    Args:

      :cmdSARG: Command to use (eg. reportsnaps, reportapps... etc.)
      :cmdArgs: Dictionary with arguments to the command

    Return:

      return a dictionary of the SARG command, mapping to the same JSON response from the API.

    Example:

      reportapps -a 1234 -x

      self.run_sarg_command("reportapps", { 'a': 1234, 'x': None })

    """

    _URI = self._sargURI

    # append the command to URI
    _URI += cmdSARG + '?'

    # append the argument
    for key in cmdArgs:
      if type(cmdArgs[key]) == dict:
        # Actifio API expects this to be urlencoded
        _URI += key + '=' + urlencode_str('&'.join([filter_key + '=' + cmdArgs[key][filter_key] for filter_key in cmdArgs[key]])) + '&'
      elif cmdArgs[key] == None:
        _URI += urlencode_str(key) + '&'
      else:
        _URI += urlencode_str(key) + '=' + urlencode_str(str(cmdArgs[key])) + '&'

    _URI += 'sessionid=' + Actifio._sessionid[self.appliance][self.username]
    try:
      sargout = self._httppool.request(
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

  def get_hosts(self, **kwargs):
    '''
    This method query for the hosts registered in Actifio applaince. You can specify a combination of following filter attributes.

    Attributes:

      :alternateip: Specifies the alternate IP address of the host. Multiple alternate can be specified in a comma-delimited list. To remove the alternate IP address, use an empty field with double quotes.
      :description: Description of the host.
      :diskpref: Specifies preference (BLOCK or NFS) for presenting the staging disk. Default value is BLOCK.
      :friendlypath: Friendly path for the host.
      :hasagent: Tells us whether the host has an agent. 0= none, 1= yes <-- this is true/false
      :hostname: Host name
      :hosttype: Host type, for example generic, hmc, hpux, hyperv, isilon, netapp svm, netapp 7 mode, openvms, tpgs, or vcenter.
      :isclusterhost: Host is a clustered host.
      :ipaddress: IP address of the host.
      :isesxhost: Whether the host is an esx server.
      :isvcenterhost: Whether the host is a management server, such as a vCenter.
      :isvm: Whether the host is a VM.
      :originalhostid: Identifies original host id for shadow host.
      :osrelease: Operating system release.
      :ostype: Operating system type.
      :osversion: Operating system version.
      :sourcecluster: Identifies the original cluster ID for shadow host
      :svcname: Specifies the SVC host name, which limits to 15 characters, first character cannot be a number, and no space, or '.' is allowed.
      :uniquename: Unique name for the host.
      :vcenterhostid: The vCenter host ID.

    Returns:

      Returns the ActHostCollection object with a list of Host entries to satisfy the filter criteria.

    '''
    try:
      if len(kwargs) > 0:
        lshost_out = self.run_uds_command('info', 'lshost', {'filtervalue': kwargs })
      else:
        lshost_out = self.run_uds_command('info', 'lshost', {})
    except:
      raise
    else:
      return ActHostCollection(self, lshost_out['result'])

  def get_applications(self, **kwargs):
    '''
    This method query for the registered applications within a Actifio applaince. You can specify a combination of following filter attributes.

    Attributes:

      :appname: Application name
      :apptype: Application type
      :appversion: Whatever we glean during discovery, and it is not always available.
      :auxinfo: For internal use, not likely to be useful.
      :description: Description of the application.
      :friendlytype: Friendly type for the application
      :hostid: Host id.
      :hostname: Host name.
      :id: Application id.
      :ignore: Allows the user to ignore the application (when set), so application will not show up in the UI.
      :isclustered: Specifies if the application is part of a cluster.
      :networkip: The network IP of the application
      :networkname: The network name of the application.
      :originalappid: Original application id.
      :pathname: The path name of the application
      :protectable:  None means you cannot protect it, fully means you can, partial means there is limited support.
      :sourcecluster:  Identifies the original cluster ID for shadow host ( when we create a shadow application or shadow host, this tells us where it originates from).

    Returns:

      Instance of ActAppCollection object with a collection of all the application matching the filter criteria.

    '''
    try:
      if len(kwargs) > 0:
        lsapplication_out = self.run_uds_command('info', 'lsapplication', {'filtervalue': kwargs})
      else:
        lsapplication_out = self.run_uds_command('info', 'lsapplication', {})
    except:
      raise
    else:
      return ActAppCollection(self, lsapplication_out['result'])

  def get_images(self, **kwargs):
    '''

    Queries Actifio appliance with matching backups images as specified by the filter criteria. if no filter criteria specified will return all the backup images.

    Args:

      :appid: Application object ID.
      :appname: Application name
      :apptype: Application type
      :backupdate: Start date [usage: 'backupdate since 24 hours' for backups started since last 24 hours,'backupdate before 7 days' for backups started older than 7 days]
      :backupname: Image name.
      :characteristic: Charchteristic for of backup type (in addition to jobclass [PRIMARY | MOUNT | UNMOUNT | VDISK | CLONE]
      :consistencydate: consistency date of the backup
      :consistency-mode: Consistency mode of image (for example, application consistent or crash consistent).
      :expiration: Date and time when this should expire. Images with an enforced retention (including remote images) cannot be expired before they reach the immutability date.
      :hostid: Application ID of the host where the backup image ??? <-- host ID of the capture job host
      :hostname: Name of the host where the backup image is???? <-- host name of the capture job host
      :jobclass: Type of jobs [ snapshot | dedup | dedupasync | clone | liveclone | syncback ]
      :label: label of the backup that user specified.
      :mappedhost: ID of the host to which backup image is mapped.
      :mountedhost: ID of host where backup image is mounted.
      :policyname: Name of the policy on which this object is created.
      :prepdate: Date when LiveClone image is created.
      :slpname: Profile name used while creating this image.
      :sltname: SLA template name used while creating this image.
      :sourceimage: obsolete
      :sourceuds: Cluster ID of the source cluster
      :targetuds: Cluster ID of the target cluster
      :virtualsize: Application size

    Returns:

      Return the backups image collection in ActImgCollection object.

    '''

    try:
      if len(kwargs) > 0:
        lsbackup_out = self.run_uds_command('info', 'lsbackup', {'filtervalue': kwargs})
      else:
        lsbackup_out = self.run_uds_command('info', 'lsbackup', {})
    except:
      raise
    else:
      return ActImageCollection(self, lsbackup_out['result'])

  def get_jobs(self, **kwargs):
    '''
    This method query for the jobs, running and archived. The following filter arguments can be used to refine the output. Returns ActJobCollection object.

    Args:

      :appid:
      :appname:
      :component:
      :enddate:
      :errorcode:
      :expirationdate:
      :hostname:
      :isscheduled:       [ true | false ]
      :jobclass:
      :jobname:
      :jobtag:
      :parentid:
      :policyname:
      :priority:
      :progress:
      :queuedate:
      :relativesize:
      :retrycount:
      :sltname:
      :startdate:
      :status:            [ running | queued | paused | interrupted | stalled ]
      :sourceid:
      :virtualsize:

    Returns:

      :doc:`ActJobCollection </actjobcollection>` object with a collection of jobs as per the selection criteria.

    '''
    try:
      lsjob_out = self.run_uds_command('info', 'lsjob', {'filtervalue': kwargs})
      lsjobhist_out = self.run_uds_command( 'info', 'lsjobhistory', {'filtervalue': kwargs})
    except:
      raise
    else:
      return ActJobsCollection(self, lsjob_out['result'] + lsjobhist_out['result'])

  def get_image_bytime(self, application, restoretime, strict_policy=False, job_class="snapshot"):
    """
    This method returns a ActImage object with a single image to the specified restore time.

    Args:

      :application: should be the application in the form of ActApplication object.
      :strict_policy: [True | False] If set to true, the image will be selected from log recovery range, with the closest image to replay the logs on.
      :restoretime: can be datetime obect or string with the format [YYYY-MM-DD HH:mm:ss] job_class: Defaults to snapshot. Should be string type, to any supported image jobclass.

    Returns:

      **ActImage** object to the specified *restoretime*. If strict_policy is set to *True*, the image will selected to the closest *restoretime*, where redo logs can be played up to the *restoretime*. If *strict_policy* is set to *False*, then the closest image to the restore time will be selected. When *strict_policy* is *False*, the recovery image consistencytime could be ahead of the *restoretime*, however *strict_policy* is True would ensure image consistency time is always lower than the *restoretime*.

    """
    from datetime import datetime
    timeformat = "%Y-%m-%d %H:%M:%S"

    if isinstance(restoretime, str):
      if restoretime != "":
        try:
          restore_time = datetime.strptime(restoretime, timeformat)
        except:
          raise ActUserError("'restoretime' need to be in the format of [YYYY-MM-DD HH:mm:ss]")
      else:
        raise ActUserError("'restoretime' should be in the type of datetime or string with format of [YYYY-MM-DD HH:mm:ss]")
    elif isinstance(restoretime, datetime):
      restore_time = restoretime
    else:
      raise ActUserError("'restoretime' should be in the type of datetime or string with format of [YYYY-MM-DD HH:mm:ss]")

    if strict_policy:
      try:
        logsmart_images = self.get_images(appid=application.id, componenttype="1")
      except:
        raise

      if len(logsmart_images) == 0:
        raise ActUserError("'strict_policy=True' is only valid for LogSmart enables applications. This application is not LogSmart enabled.")
      else:
        ls_image = logsmart_images[0]
        ls_image.details()
        try:
          viable_images = self.get_images(appid=application.id, consistencydate=">" + ls_image.beginpit, jobclass=job_class)
        except:
          raise

      prefered_image = None
      prefered_image_time = None

      for img in viable_images:
        try:
          consistency_time = datetime.strptime(img.consistencydate[:-4], timeformat)
        except:
          raise
        if prefered_image is None:
          if consistency_time < restore_time:
            prefered_image = img
            prefered_image_time = consistency_time
        else:
          if prefered_image_time < consistency_time < restore_time:
            prefered_image = img
            prefered_image_time = consistency_time

      return prefered_image
    else:
      try:
        app_images = self.get_images(appid=application.id, jobclass=job_class)
      except:
        raise

      shortest_gap = None
      prefered_image = None
      prefered_image_time = None

      for img in app_images:
        try:
          consistency_time = datetime.strptime(img.consistencydate[:-4], timeformat)
        except:
          raise

        if prefered_image is None:
          # print("processing first image")
          prefered_image = img
          prefered_image_time = consistency_time
          # print( str(consistency_time)+ "  -  " + str(restore_time))
          if consistency_time > restore_time:
            # print( "consistency time is later than restore time")
            shortest_gap = consistency_time - restore_time
          else:
            shortest_gap = restore_time - consistency_time
            # print( "restore time is later than consistency ")
        else:
          # print("first image is already set")
          # print( str(consistency_time)+ "  -  " + str(prefered_image_time))
          if consistency_time > restore_time:
            # print( "consistency time is later than prefered image time")
            this_image_gap = consistency_time - restore_time
          else:
            # print( "prefered image time is later than consistency ")
            this_image_gap = restore_time - consistency_time

          if shortest_gap.total_seconds() > this_image_gap.total_seconds():
            # print("prefered image time is :" + str(consistency_time))
            prefered_image = img
            prefered_image_time = consistency_time
            shortest_gap = this_image_gap

      return prefered_image

  def clone_database(self, source_hostname, source_appname, target_hostname, restoretime="", strict_policy=True, **kwargs):
    '''

    This method creates a virtual clone of Oracle or SQL server database.

    Agrs:

      :source_hostname: Hostname of the source host where the database was captured from
      :source_appname: source application name, or the database name
      :target_hostname: target host where the virtual clone need to be created on

      *Miscelaneous Parameters*

      :restoretime: Point in time the database needs to be recovered to.
      :strict_policy: Defaults to True, If set to True (only for applications with log database backups), :databases will be cloned to the time specified.
      :nowait: defaults to True, if True, this method will be non-blocking mode.

      *Oracle Related Parameters*

      :oracle_home (required): ORACLE_HOME
      :oracle_db_name (required): SID of the target clone
      :oracle_user (optional): Defaults to "oracle".
      :oracle_tns_admin (optional): TNS admin path, defaults to $ORACLE_HOME/network/admin.
      :oracle_db_mem (optional): Total Memory Target for the database, defaults to 512MB.
      :oracle_sga_pct (optional): Memory Percentage to allocate for SGA
      :oracle_redo_size (optional): Redo Log size in MB, defaults to 500
      :oracle_shared_pool (optional): Oracle Shared Pool size
      :oracle_db_cache_size (optional): Oracle DB Cache size
      :oracle_recover_dest_size (optional): Oracle Parameter db_recover_dest_size. Defaults to 5000
      :oracle_diagnostic_dest (optional): Oracle Diagnostic Destination
      :oracle_nprocs (optional): Num of Max processes
      :oracle_open_cursors (optional): Number of open_cursors. defaults to 1000.
      :oracle_char_set (optional): Characterset. Defaults to 'AL32UTF8'
      :oracle_tns_ip (optional): TNS IP Address
      :oracle_tns_port (optional): TNS Port
      :oracle_tns_domain (optional): TNS Domain
      :oracle_no_nid (optional): Do not change the DBID of the new clone. Will maintain same DBID as the source. Defaults to FALSE
      :oracle_no_tns_update (optional): Do not update TNS records. Defaults to FALSE
      :oracle_restore_recov (optional): Recover the oracle database. Defaults to TRUE
      :oracle_no_rac (optional): Treat as Oracle RAC. Defaults to TRUE

      *SQLServer Related*

      :sql_instance_name (required): Target SQL Server instance name
      :sql_recover_userlogins (optional): Recover user logins of the database. Defaults to FALSE
      :sql_username (optional): Username for database provisioning
      :sql_password (optional): Password for the specified user

      *SQLServer DB Application*

      :sql_db_name (reuired): Database name at the target instance. (Only required if the source application is database or single database mount from instance.)

      *SQLServer Instance*

      :sql_source_dbnames (required): Source database names if the source application is SQL instance. Use ',' as delimiter for multiple databases. (Only required if the source application is SQL server instance.)
      :sql_cg_name (required): Consistency group name. (Only required if the source application is SQL Server instance and mount multiple databases at a time.)
      :sql_dbname_prefix (optional): Prefix of database name for multiple database mount
      :sql_dbname_suffix (optional): Suffix of database name for multiple database mount

    Returns:

      This method returns a tuple of (ActJob,ActImage), respectively the resulting Job and Image.

    '''
    # parse kwargs

    kwarg_map = {
      'orahome': 'oracle_home',
      'username': 'oracle_username',
      'databasesid': 'oracle_db_name',
      'tnsadmindir': 'oracle_tns_admin',
      'totalmemory': 'oracle_db_mem',
      'sgapct': 'oracle_sga_pct',
      'redosize': 'oracle_redo_size',
      'shared_pool_size': 'oracle_shared_pool',
      'db_cache_size': 'oracle_db_cache_size',
      'db_recovery_file_dest_size': 'oracle_recover_dest_size',
      'diagnostic_dest': 'oracle_diagnostic_dest',
      'processes': 'oracle_nprocs',
      'open_cursors': 'oracle_open_cursors',
      'characterset': 'oracle_char_set',
      'tnsip': 'oracle_tns_ip',
      'tnsport': 'oracle_tns_port',
      'tnsdomain': 'oracle_tns_domain',
      'nonid': 'oracle_no_nid',
      'notnsupdate': 'oracle_no_tns_update',
      'rrecovery': 'oracle_restore_recov',
      'standalone': 'oracle_no_rac'
    }

    def __parse_kwargs(key):
      try:
        if kwargs[kwarg_map[key]] != "":
          return kwargs[kwarg_map[key]]
      except KeyError:
        if key == "username":
          return "oracle"
        elif key == "tnsadmindir":
          return kwargs['oracle_home']+"/network/admin"
        else:
          return None
      except:
        raise

    # Strict policy
    try:
      if isinstance(kwargs['strict_policy'], bool):
        strict_policy = kwargs['strict_policy']
      else:
        raise ActUserError("'strict_policy' should be boolean")
    except KeyError:
      strict_policy = False

    # restore time validation routines (same as get_image_bytime)
    from datetime import datetime
    timeformat = "%Y-%m-%d %H:%M:%S"

    if isinstance(restoretime, str):
      if restoretime != "":
        try:
          restore_time = datetime.strptime(restoretime, timeformat)
        except:
          raise ActUserError("'restoretime' need to be in the format of [YYYY-MM-DD HH:mm:ss]")
    elif isinstance(restoretime, datetime):
      restore_time = restoretime
    else:
      raise ActUserError("'restoretime' should be in the type of datetime or string with format of [YYYY-MM-DD HH:mm:ss]")

    try:
      source_application = self.get_applications(appname=source_appname, hostname=source_hostname, apptype="not VMBackup")
    except:
      raise

    if len(source_application) < 1:
      raise ActUserError("Unable to find the 'source_application' application: " + source_application)

    provisioningoptions = ""
    mountimage_args = {}
    # if source_application[0].appclass == "Oracle":
    try:
      app_parameters = self.run_uds_command("info", "lsappclass", {"name": source_application[0].appclass})
    except:
      raise

    # print(type(app_parameters))
    for param in app_parameters['result']:
      if __parse_kwargs(param['name']) is not None:
        provisioningoptions += "<" + str(param['name']) + ">" + __parse_kwargs(param['name']) + "</" + str(param['name']) + ">"
    if source_application[0].appclass == "SQLServerGroup":
      if __parse_kwargs("sql_source_dbnames") is not None and len(__parse_kwargs("sql_source_dbnames").split(',')) == 1:
        provisioningoptions += "<dbname>" + __parse_kwargs("sql_source_dbnames") + "</dbname>"

    provisioningoptions = "<provisioningoptions>" + provisioningoptions + "</provisioningoptions>"

    # print(provisioningoptions)

    mountimage_args.__setitem__('restoreoption', {'provisioningoptions': provisioningoptions})

    try:
      target_host = self.get_hosts(hostname=target_hostname)
    except:
      raise

    if len(target_host) != 1:
      raise ActUserError("Unable to find the specified 'target_hostname': " + target_hostname)

    mountimage_args.__setitem__('host', target_host[0].id)

    # get the image by recovery time

    if restoretime == "":
      mountimage_args.__setitem__('appid', source_application[0].id)
    else:
      try:
        mount_image = self.get_image_bytime(source_application[0], restoretime, strict_policy)
      except:
        raise
      else:
        mountimage_args.__setitem__('image', str(mount_image))

    # handling no wait

    try:
      if kwargs['nowait'] != "":
        kwargs_nowait = kwargs['nowait']
      else:
        kwargs_nowait = True
    except KeyError:
      kwargs_nowait = True

    if kwargs_nowait:
      mountimage_args.__setitem__('nowait', None)

    # mountimage steps
    # print (mountimage_args)
    mountimage_out = self.run_uds_command("task", "mountimage", mountimage_args)

    result_job_name = mountimage_out['result'].split(" ")[0]
    result_image_name = mountimage_out['result'].split(" ")[3]

    return (self.get_jobs(jobname=result_job_name)[0], self.get_images(backupname=result_image_name))

  def simple_mount(self, source_application=None, target_host=None, mount_image=None,
  restoretime="", strict_policy=False, pre_script="", post_script="", nowait=True,
  job_class="snapshot", mount_mode="", label="Python Library", **kwargs):
    """

    This method mounts a simple mount operation, for a application type. This mount will not create a
    virtual clone (if you need to create a virtual clone look into clone_database() instead).

    Args:

      *If not mount_image is None*

      :mount_image (required): ActImage object refering to mount image

      *ElseIf not source_application is None*

      :source_hostname (required): hostname where the server was backed up from.
      :source_appname (required): name of the application

      *Else*

      :source_application (required): ActApplication object refereing to source application

      *If not target-host is None*

      :target_hostname (required): hostname of the target host

      *Else*

      :target_host (required): ActHost object refering to the target host

      :restoretime (optional): recovery time of the mount image, depending on the strict_policy, the closest image will be selected.
      :strict_policy (optional): Boolean, defaults to False, if True, application is treated as transaction log capable and image is selected to a level where recoverable to restoretime. Else closest image to the time will be selected

      :pre_script (optional): Pre Script for the mount operation
      :post-script (optional): Post Script for the mount operation
      :nowait (optional): defaults to True, mount job will not wait till the completion, if False,
                         this method will be blocking until the job completion.
      :job_class (optional): Defaults to "snapshot", valid jobclasses are, [ snapshot | dedup |
                            dedupasync | OnVault ]. job_class is applicable only when the restoretime is specified.
      :mount_mode (optional): Takes the value, physical (pRDM), independentvirtual (vRDM), or nfs (requires 9.0)
      :maptoallesxhosts (optional): Defaults to False. Map to all the ESXi hosts in the cluster.

      *Restore Options*

      Any of the restoreoptions as listed in the **udsinfo lsrestoreoptions** can be specified as key=value command arguments.

      .. note:: For more information on the restore options refer to the Appendix F on the RESTfulAPI.pdf.

    Returns:

      This method returns a tuple of (ActJob,ActImage), respectively the resulting Job and Image.


      returns a Tuple with (ActJob , ActImage):


    """

    mountimage_args = {}

    if source_application is None:
      raise ActUserError("'source_application' is not specified.")

    if restoretime == "":
      mountimage_args.__setitem__('appid', source_application.id)
      # still we need a image to generate the restoreoptions
      mount_image = self.get_images(appid=source_application.id)[0]
      # TODO: This is a costly approch to get a single image. Need to come up with a better
      # approach
    else:
      if mount_image is None:
        mount_image = self.get_image_bytime(source_application, restoretime, strict_policy, job_class)

        if mount_image is None:
          raise ActUserError("Unable to find a suitable image for the 'restoretime' and 'strict_policy' criteria.")

      mountimage_args.__setitem__('image', mount_image.imagename)

    if isinstance(target_host, ActHost):
      mountimage_args.__setitem__('host', target_host.id)
    else:
      raise ActUserError("'target_host' need to be specified and ecpects ActHost object")

    if nowait:
      mountimage_args.__setitem__('nowait', None)

    script_data = []

    if pre_script != "":
      script_data.append('name='+pre_script+':phase=PRE')

    if post_script != "":
      script_data.append('name='+post_script+':phase=POST')

    if len(script_data) != 0:
      mountimage_args.__setitem__('script', ';'.join(script_data))

    if mount_mode in ['physical', 'independentvirtual', 'nfs']:
      if self._minimum_version("9.0.0.0"):
        mountimage_args.__setitem__('rdmmode', mount_mode)
      else:
        if mount_mode == "physical":
          mountimage_args.__setitem__('physicalrdm', None)
        elif mount_mode == "nfs":
          sys.stderr.write("RDM Mode for nfs requires minimum Actifio 9.0.0\n")
    else:
      raise ActUserError("'mount_mode' should be from ['physical', 'independentvirtual', 'nfs']")

    # get the list of restore options

    restoreopts = mount_image.restoreoptions('mount', target_host)

    restoreopts_data = []

    for opt in restoreopts:
      kwargs_opt = kwargs.get(opt.name)
      if kwargs_opt is not None:
        restoreopts_data.append(opt.name + "-" +  + "=" + str(kwargs_opt))

    if len(restoreopts_data) != 0:
      mountimage_args.__setitem__('restoreoption', ','.join(restoreopts_data))

    mountimage_out = self.run_uds_command('task', 'mountimage', mountimage_args)

    result_job_name = mountimage_out['result'].split(" ")[0]
    result_image_name = mountimage_out['result'].split(" ")[3]

    return (self.get_jobs(jobname=result_job_name)[0], self.get_images(backupname=result_image_name)[0])
