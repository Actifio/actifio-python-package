import sys
if sys.version [:3] == "2.7":
  import exceptions

class ActException (Exception):
  def __init__(self, message):
    super(ActException, self).__init__(message)
    self.message = message
    self.error_code = ""

# this is still supported in 3.7
  def __str__(self):
    if self.error_code != "":
      return "[" + self.error_code + "] " + self.message
    else:
      return self.message

class ActLoginError(ActException):
  def __init__(self, msg):
    Exception.__init__(self, "Actifio Login Exception: " + str(msg))
    self.msg = msg

class ActConnectError (ActException):
  def __init__(self, msg):
    Exception.__init__(self, "Actifio Connection Error: " + str(msg))
    self.msg = msg

class ActAPIError (ActException):
  def __init__(self, msg, error_code):
    Exception.__init__(self, "Actifio API Error: " + str(msg))
    self.msg = msg
    self.error_code = error_code

class ActUserError (ActException):
  def __init__(self, msg):
    Exception.__init__(self, "Actifio User Error: " + str(msg))
    self.msg = msg

class ActVersionError (ActException):
  def __init__(self, object_name, min_version):
    Exception.__init__(self, "Actifio Version Error: The " + str(object_name) + " is not supported with the current version: min version == " + str(min_version))
    self.object_name = object_name
    self.min_version = min_version