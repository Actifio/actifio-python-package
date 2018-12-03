from Actifio import Actifio as Act

class ActEnforce():
  @classmethod
  def needs_token(cls,act_func):
    @wraps(act_func)
    def decorated(cls, *args, **kwargs):
      try:
        if cls._sessionid == '':
          Act._create_session(cls)
        result = act_func(cls,*args, **kwargs)
      except:
        if not Act._validate_token(cls):
          Act._create_session(cls)
          try:
            result = act_func(cls,*args, **kwargs)
          except:
            raise
          else:
            return result
        else:
          raise
      else:
        return result
    return decorated
