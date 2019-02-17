'''

Support classes to handle Actifio Object endpoints. 

'''

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

  def get(self, parameter):
    return self.objectdata[parameter]

  def refresh (self):
    pass

  def details(self):
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

class ActHostCollection(ActObjCollection):
  def __init__(self, appliance, lshostdata):
    return super(ActHostCollection, self).__init__("hosts", ActHost, appliance, lshostdata)

############# Applications Related ###############

class ActApplication(ActObject):
  def __init__(self, applaince, appdata):
    super(ActApplication, self).__init__(applaince, appdata, appdata['appname'], appdata['id'])

class ActAppCollection(ActObjCollection):
  def __init__(self, appliance, lsapplicationdata):
    return super(ActAppCollection, self).__init__("applications", ActApplication, appliance, lsapplicationdata)

############# Image Related ######################

class ActImage(ActObject):
  def __init__(self, applaince, imgdata):
    super(ActImage, self).__init__(applaince, imgdata, imgdata['backupname'], imgdata['id'])

class ActImageCollection(ActObjCollection):
  def __init__(self, appliance, lsbackupdata):
    return super(ActImageCollection, self).__init__("images", ActImage, appliance, lsbackupdata)

############## Jobs Related ######################

class ActJob(ActObject):
  def __init__(self, applaince, jobdata):
    super(ActJob, self).__init__(applaince, jobdata, jobdata['jobname'], jobdata['id'])

  def refresh(self):
    """
    Method to refresh t
    """
    try:
      this_job = self.appliance.run_uds_command('info','lsjob',{ "argument": self.get('id')})
    except:
      raise

    if len(this_job['result']) == 0:
      try:
        this_job = self.appliance.run_uds_command('info','lsjobhistory',{ "argument": self.get('id') })
      except:
        raise
    else:
      self.__init__(self.appliance, this_job['result'])


class ActJobsCollection(ActObjCollection):
  def __init__(self, appliance, lsjobsalldata):
    return super(ActJobsCollection, self).__init__("jobs", ActJob, appliance, lsjobsalldata)

