# Actifio Python Client Library

This is a python package to handle Actifio RestAPI. Package wraps around the Rest API to facilitate for UDS and SARG functions. Package also provides functionality for higher functions.

# Install

To install, we always recomend to use ```pip```.

```
pip install Actifio
```

# Documentation

You can find the documentation here.


# Current Implemented Methods


## Actifio.run_uds_command(cmdType, cmdUDS, cmdArgs) 

Run UDS command, for udsinfo and udstask commands. 

  **CmdType** : Command Type takes either ```info``` or ```task``` as options (string)

  **cmdUDS**  : UDS command, as you would use in the CLI.

  **cmdArgs** : Arguments for the UDS command. This option takes arguments as a dictionary.
               For example:

               vmdiscovery -discovercluster -host 1234 
               { 'discovercluster': None, 'host': "1234" }

               lsapplication -filtervalues "appname=mydb&hostname=myhost"
               { 'filtervalues': { 'appname': 'mydb', 'hostname': 'myhost' } }

               lshost 123
               { 'argument': "123" }

               RESTfulAPI_*.pdf would be good referecne point for the __SIMILARITY__ and 
               __PATTERN__.

### Return

This method will return the output of the command in dictionary. 

  **cmdSARG** : SARG Command 

### Example: 

```
try: 
  udsout = act.run_uds_command('info','lshost', { "filtervalue": { "hostname": "orademodb"} })
except Exception as e:
  print(e)
else:
  print(udsout['result'][0]['id'])
```

## Actifio.run_sarg_command() 

Run report commands for SARG. 


# How to use?



```
from Actifio import Actifio


act = Actifio('MyActifioAppliance','admin','password','xxxx-xxxx-xxxx-xxxx')

try:
  sargout = act.run_sarg_command('reportapps', { 'a': 'mydb'})
except Exception as e:
  print (e)
else:
  print(sargout) 

try: 
  udsout = act.run_uds_command('info','lshost', { "filtervalue": { "hostname": "orademodb"} })
except Exception as e:
  print(e)
else:
  print(udsout['result'][0]['id'])
```

License
-------

Copyright 2018 <Kosala Atapattu kosala.atapattu@actifio.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
