import sys

class ActException (Exception):
  def __init__(self, message, code):
    super(ActException, self).__init__(message, code)
    self.message = message
    self.error_code = code

# this is still supported in 3.8
  def __str__(self):
    if self.error_code is not None:
      return "[" + str(self.error_code) + "] " + self.message
    else:
      return self.message

class ActLoginError(ActException):
  def __init__(self, message):
    super().__init__("Actifio Login Exception: " + str(message), None)

class ActConnectError (ActException):
  def __init__(self, message):
    super().__init__("Actifio Connection Error: " + str(message), None)

class ActAPIError (ActException):
  def __init__(self, message, error_code):
    super().__init__("Actifio API Error: " + str(message), error_code)

class ActUserError (ActException):
  def __init__(self, message):
    super().__init__( "Actifio User Error: " + str(message), None)

class ActVersionError (ActException):
  def __init__(self, object_name, min_version):
    super().__init__("Actifio Version Error: The " + str(object_name) + " is not supported with the current version: min version == " + str(min_version), None)
    self.object_name = object_name
    self.min_version = min_version