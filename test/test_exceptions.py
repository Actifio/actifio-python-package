import unittest
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

if __name__ == "__main__":
  unittest.main()
