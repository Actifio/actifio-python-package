import unittest
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))

from Actifio import Actifio 
from Actifio.actexceptions import *

appliance = os.environ['APPLIANCE']
user = os.environ['ACTUSER']
password = os.environ['ACTPASS']

agm = os.environ['ACTAGM']

wrong_applaince = os.environ['WRONGAPPLIANCE']
wrong_user = os.environ['WRONGUSER']
wrong_password = os.environ['WRONGPASS']

oracle_db = os.environ['ORADB']
ora_source = os.environ['ORASOURCE']
ora_target = os.environ['ORATARGET']

sql_db = os.environ['SQLDB']
sql_source = os.environ['SQLSOURCE']
sql_target = os.environ['SQLTARGET']


class ExceptionTesting(unittest.TestCase):
  def test_incorrect_ip(self):
    with self.assertRaises(ActConnectError):
      act = Actifio(wrong_applaince, user, password)
      act.run_uds_command('info', 'lsversion', {})

  def test_wrong_appliance(self):
    with self.assertRaises(ActLoginError) as excp:
      act = Actifio(agm, user, password)
      act.run_uds_command('info', 'lsversion', {})
    self.assertEqual(excp.exception.msg, "This does not seem to be a Actifio Sky/CDS appliance")

  def test_wrong_user(self):
    with self.assertRaises(ActLoginError) as excp:
      act = Actifio(appliance, wrong_user, password)
      act.run_uds_command('info', 'lsversion', {})
    self.assertEqual(excp.exception.msg, "Invalid username or password")

  def test_wrong_password(self):
    with self.assertRaises(ActLoginError) as excp:
      act = Actifio(appliance, user, wrong_password)
      act.run_uds_command('info', 'lsversion', {})
    self.assertEqual(excp.exception.msg, "Invalid username or password")

  def test_incorrect_command(self):
    with self.assertRaises(ActAPIError) as excp:
      act = Actifio(appliance, user, password)
      act.run_uds_command('info', 'lsversion2', {})

    with self.assertRaises(ActAPIError) as excp:
      act = Actifio(appliance, user, password)
      act.run_uds_command('xxx', 'lsversion', {})

  def test_get_image_bytime_args(self):
    act = Actifio(appliance, user, password)
    oracleapp = act.get_applications(appname=oracle_db, hostname=ora_source, appclass="Oracle")
    sqlapp = act.get_applications(appname=sql_db, hostname=sql_source, appclass="SQLServer")
    nonlsapp = act.get_applications(friendlytype="VMBackup")

    # incorrect restoretime format in string
    with self.assertRaises(ActUserError) as excp:
      from datetime import datetime      
      act.get_image_bytime(
        application=oracleapp[0], 
        restoretime="03-12-2234 00:00:00",
        strict_policy=True 
        )
    self.assertEqual(excp.exception.msg, "'restoretime' need to be in the format of [YYYY-MM-DD HH:mm:ss]")

    # strict_policy with non LogSmart app
    with self.assertRaises(ActUserError) as excp:
      from datetime import datetime      
      act.get_image_bytime(
        application=nonlsapp[0], 
        restoretime=datetime.today(),
        strict_policy=True 
        )
    self.assertEqual(excp.exception.msg, "'strict_policy=True' is only valid for LogSmart enables applications. This application is not LogSmart enabled.")

    # restoretime can't be empty
    with self.assertRaises(ActUserError) as excp:
      from datetime import datetime      
      act.get_image_bytime(
        application=oracleapp[0], 
        restoretime="",
        strict_policy=True 
        )
    self.assertEqual(excp.exception.msg, "'restoretime' should be in the type of datetime or string with format of [YYYY-MM-DD HH:mm:ss]")


if __name__ == "__main__":
  unittest.main()
