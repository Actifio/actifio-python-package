import sys
if sys.version [:3] == "2.7":
  import exceptions

class ActLoginError(Exception):
  def __init__(self, msg):
    Exception.__init__(self, "Actifio Login Exception: " + str(msg))
    self.msg = msg

class ActConnectError (Exception):
  def __init__(self, msg):
    Exception.__init__(self, "Actifio Connection Error: " + str(msg))
    self.msg = msg

class ActAPIError (Exception):
  def __init__(self, msg):
    Exception.__init__(self, "Actifio API Error: " + str(msg))
    self.msg = msg

class ActUserError (Exception):
  def __init__(self, msg):
    Exception.__init__(self, "Actifio User Error: " + str(msg))
    self.msg = msg

class ActVersionError (Exception):
  def __init__(self, object_name, min_version):
    Exception.__init__(self, "Actifio Version Error: The " + str(object_name) + " is not supported with the current version: min version == " + str(min_version))
    self.object_name = object_name
    self.min_version = min_version