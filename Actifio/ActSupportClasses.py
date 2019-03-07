'''

Support classes to handle Actifio Object endpoints. 

'''
import sys

# import auxialary libraries 
if sys.version [:3] == "2.7":
  from actexceptions import *
elif sys.version[0] == "3":
  from Actifio.actexceptions import *


############# Base Class for all ################

class ActObject ():
  def __init__(self, appliance, objectData, printable, uniqueid):
    """
    Initiator forthe ActObjeect. This will be a base class for all the other Actifio Object types

    appliance: Actifio object, which generated this object
    objectData: Data to be loaded to this actifio Object

    """
    self.objectdata = objectData
    self.printable = printable
    self.appliance = appliance
    self.id = uniqueid

  def __str__(self):
    return self.printable

  def __getattr__(self, name):
    try:
      return self.objectdata[name]
    except KeyError:
      raise ActUserError ("There is no parameter: " + name)

  def get(self, parameter):
    try:
      return self.objectdata[parameter]
    except KeyError:
      raise ActUserError ("There is no parameter: " + parameter)

  def refresh (self):
    pass

class ActObjCollection ():
  def __init__(self, objecttype, retobject, appliance, objectData):
    """
    This is the base object class for all the Actifio support object types.

    objecttype: is a string variable to describe the type of objects to contain in this object collection
    retobject: __next__ and __getitem__ return this type of objects.
    appliane: actifio object which generated this object collections.
    objectData: data for the objects

    """
    self.objectdata = objectData
    self.objtype = objecttype
    self.returnobj = retobject
    self.appliance = appliance

  def __str__(self):
    return "Collection of " + str(len(self)) + " " + self.objtype + "."

  def __iter__(self):
    return self.ActObjIterator(self)

  def __len__(self):
    return len(self.objectdata)

  def __getitem__(self,_index):
    return self.returnobj(self.appliance, self.objectdata[_index])
  
  class ActObjIterator:
    def __init__(self, ObjectCollection):
      self.objCollection = ObjectCollection
      self._index = 0

    def __iter__(self):
      return self

    def __next__(self):
      if self._index < len(self.objCollection):
        return_object = self.objCollection.returnobj(self.objCollection.appliance, self.objCollection.objectdata[self._index])
        self._index += 1
        return return_object
      else:
        raise StopIteration

    # python2.7 support
    next = __next__
  

############## Hosts Related ######################

class ActHost(ActObject):
  def __init__(self, applaince, hostdata):
    super(ActHost, self).__init__(applaince, hostdata, hostdata['hostname'], hostdata['id'])

  def details(self):
    host_details = self.appliance.run_uds_command("info","lshost",{ "argument" : self.id })
    self.objectdata = host_details['result'] 


class ActHostCollection(ActObjCollection):
  def __init__(self, appliance, lshostdata):
    return super(ActHostCollection, self).__init__("hosts", ActHost, appliance, lshostdata)

############# Applications Related ###############

class ActApplication(ActObject):
  def __init__(self, applaince, appdata):
    super(ActApplication, self).__init__(applaince, appdata, appdata['appname'], appdata['id'])

  def details(self):
    app_details = self.appliance.run_uds_command("info","lsapplication",{ "argument" : self.id })
    self.objectdata = app_details['result'] 

class ActAppCollection(ActObjCollection):
  def __init__(self, appliance, lsapplicationdata):
    return super(ActAppCollection, self).__init__("applications", ActApplication, appliance, lsapplicationdata)

############# Image Related ######################

class ActImage(ActObject):
  def __init__(self, applaince, imgdata):
    super(ActImage, self).__init__(applaince, imgdata, imgdata['backupname'], imgdata['id'])

  def details(self):
    image_details = self.appliance.run_uds_command("info","lsbackup",{ "argument" : self.id })
    self.objectdata = image_details['result'] 

class ActImageCollection(ActObjCollection):
  def __init__(self, appliance, lsbackupdata):
    return super(ActImageCollection, self).__init__("images", ActImage, appliance, lsbackupdata)

############## Jobs Related ######################

class ActJob(ActObject):
  def __init__(self, applaince, jobdata):
    super(ActJob, self).__init__(applaince, jobdata, jobdata['jobname'], jobdata['id'])

  def refresh(self):
    """
    Method to refresh the job details.
    """

    if self.status == 'running' or self.status == 'waiting':
      try:
        this_job = self.appliance.run_uds_command('info','lsjob',{ 'filtervalue' : { 'jobname': str(self) } } )
      except:
        pass

      if len(this_job['result']) == 0:
        try:
          this_job = self.appliance.run_uds_command(  'info','lsjobhistory',{ 'filtervalue' : { 'jobname': str(self) } } )
        except:
          raise
      
      self.__init__(self.appliance, this_job['result'][0])


class ActJobsCollection(ActObjCollection):
  def __init__(self, appliance, lsjobsalldata):
    return super(ActJobsCollection, self).__init__("jobs", ActJob, appliance, lsjobsalldata)

  def refresh(self):
    """
    Method to refresh the job details, for each job.
    """

    for job in self:
      job.refresh()

