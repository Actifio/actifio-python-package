class ActException(Exception):
  def __init__(self, message):
    super(ActException, self).__init__(message)
    self.message = message

class ActLoginError(ActException):
  def __init__(self, msg):
    super(ActLoginError, self).__init__('Actifio Login Exception: %s' %  msg)
    self.msg = msg

class ActConnectError(ActException):
  def __init__(self, msg):
    super(ActConnectError, self).__init__('Actifio Connection Error: %s' %  msg)
    self.msg = msg

class ActAPIError(ActException):
  def __init__(self, msg, error_code=''):
    if error_code != '':
      super(ActAPIError, self).__init__('[%s] Actifio API Error: %s' %  (error_code, msg))
    else:
      super(ActAPIError, self).__init__('Actifio API Error: %s' %  msg)
    self.msg = msg
    self.error_code = error_code

class ActUserError(ActException):
  def __init__(self, msg):
    super(ActUserError, self).__init__('Actifio User Error: %s' %  msg)
    self.msg = msg

class ActVersionError(ActException):
  def __init__(self, object_name, min_version):
    super(ActVersionError, self).__init__('Actifio Version Error: "%s" is not supported with the current version. Min version == %s' %  (object_name, min_version))
    self.object_name = object_name
    self.min_version = min_version
