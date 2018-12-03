# actifio-python-package

This is a python package handle Actifio RestAPI. 

# How to use?

```
from Actifio import Actifio

act_uds = Actifio('MyActifioAppliance','admin','password','xxxx-xxxx-xxxx-xxxx')
act_sarg = Actifio('MyActifioAppliance','admin','password','xxxx-xxxx-xxxx-xxxx')

try:
  sargout = act_sarg.run_sarg_command('reportapps', { 'a': 'mydb'})
except Exception as e:
  print (e)
else:
  print(sargout) 

try: 
  udsout = act_uds.run_uds_command('info','lshost', { "filtervalue": { "hostname": "orademodb"} })
except Exception as e:
  print(e)
else:
  print(udsout['result'][0]['id'])
```