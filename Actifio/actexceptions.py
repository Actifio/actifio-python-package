import sys
if sys.version [:3] == "2.7":
  import exceptions

class ActLoginError(Exception):
  def __init__(self, msg):
    Exception.__init__(self, "Actifio Login Exception: " + str(msg))

class ActConnectError (Exception):
  def __init__(self, msg):
    Exception.__init__(self, "Actifio Connection Error: " + str(msg))

class ActAPIError (Exception):
  def __init__(self, msg):
    Exception.__init__(self, "Actifio API Error: " + str(msg))

class ActUserError (Exception):
  def __init__(self, msg):
    Exception.__init__(self, "Actifio User Error: " + str(msg))