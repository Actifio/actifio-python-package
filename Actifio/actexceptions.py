import sys
if sys.version [:3] == "2.7":
  import exceptions

class ActLoginError(Exception):
  def __init__(self, msg):
    Exception.__init__(self, msg)

class ActConnectError (Exception):
  def __init__(self, msg):
    Exception.__init__(self, msg)

class ActAPIError (Exception):
  def __init__(self, msg):
    Exception.__init__(self, msg)
