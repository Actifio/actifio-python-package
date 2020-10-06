import unittest
import os
import sys
# sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))

from Actifio import Actifio 
from Actifio.actexceptions import *

print(sys.modules[ActAPIError.__module__].__file__)

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
ora_home = os.environ['ORACLE_HOME']
ora_dbname = os.environ['ORACLE_SID']

sql_db = os.environ['SQLDB']
sql_dbinst = os.environ['SQLDBINST']
sql_db_source = os.environ['SQLSOURCE']
sql_db_target = os.environ['SQLTARGET']

sql_inst = os.environ['SQLINST']
sql_inst_inst = os.environ['SQLTARGETINST']
sql_inst_source = os.environ['SQLINSTSOURCE']
sql_inst_target = os.environ['SQLINSTTARGET']


class ExceptionTesting(unittest.TestCase):
  def test_incorrect_ip(self):
    with self.assertRaises(ActConnectError):
      act = Actifio(wrong_applaince, user, password)
      act.run_uds_command('info', 'lsversion', {})

  def test_wrong_appliance(self):
    with self.assertRaises(ActLoginError) as excp:
      act = Actifio(agm, user, password)
      act.run_uds_command('info', 'lsversion', {})
    self.assertEqual(str(excp.exception), "Actifio Login Exception: This does not seem to be a Actifio Sky/CDS appliance")

  def test_missing_user_token (self):
    with self.assertRaises(ActLoginError) as excp:
      act = Actifio(appliance, wrong_user, password)
      act.run_uds_command('info', 'lsversion', {})
    self.assertEqual(str(excp.exception), "Actifio Login Exception: Invalid username or password")

  def test_wrong_user(self):
    with self.assertRaises(ActLoginError) as excp:
      act = Actifio(appliance, wrong_user, password)
      act.run_uds_command('info', 'lsversion', {})
    self.assertEqual(str(excp.exception), "Actifio Login Exception: Invalid username or password")

  def test_wrong_password(self):
    with self.assertRaises(ActLoginError) as excp:
      act = Actifio(appliance, user, wrong_password)
      act.run_uds_command('info', 'lsversion', {})
    self.assertEqual(str(excp.exception), "Actifio Login Exception: Invalid username or password")

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
    sqlapp = act.get_applications(appname=sql_db, hostname=sql_db_source, appclass="SQLServer")
    nonlsapp = act.get_applications(friendlytype="VMBackup")

    # incorrect restoretime format in string
    with self.assertRaises(ActUserError) as excp:
      from datetime import datetime      
      act.get_image_bytime(
        application=oracleapp[0], 
        restoretime="03-12-2234 00:00:00",
        strict_policy=True 
        )
    self.assertEqual(str(excp.exception), "Actifio User Error: 'restoretime' need to be in the format of [YYYY-MM-DD HH:mm:ss]")

    # strict_policy with non LogSmart app
    with self.assertRaises(ActUserError) as excp:
      from datetime import datetime      
      act.get_image_bytime(
        application=nonlsapp[0], 
        restoretime=datetime.today(),
        strict_policy=True 
        )
    self.assertEqual(str(excp.exception), "Actifio User Error: 'strict_policy=True' is only valid for LogSmart enables applications. This application is not LogSmart enabled.")

    # restoretime can't be empty
    with self.assertRaises(ActUserError) as excp:
      from datetime import datetime      
      act.get_image_bytime(
        application=oracleapp[0], 
        restoretime="",
        strict_policy=True 
        )
    self.assertEqual(str(excp.exception), "Actifio User Error: 'restoretime' should be in the type of datetime or string with format of [YYYY-MM-DD HH:mm:ss]")

  def test_clone_database_args(self):
    act = Actifio(appliance, user, password)
    oracleapp = act.get_applications(appname=oracle_db, hostname=ora_source, appclass="Oracle")
    sqldb = act.get_applications(appname=sql_db, hostname=sql_db_source , appclass="SQLServer")
    sqlinst = act.get_applications(appname=sql_inst, appclass="SQLServerGroup")
    nonlsapp = act.get_applications(friendlytype="VMBackup")
    target_host_ora = act.get_hosts(hostname=ora_target)

    # incorrect restoretime format in string
    with self.assertRaises(ActUserError) as excp:
      from datetime import datetime      
      act.clone_database(
        source_application=oracleapp[0], 
        restoretime="03-12-2234 00:00:00",
        target_host=target_host_ora,
        strict_policy=True,
        ora_home=ora_home,
        ora_dbname=ora_dbname 
        )
    self.assertEqual(str(excp.exception), "Actifio User Error: 'restoretime' need to be in the format of [YYYY-MM-DD HH:mm:ss]")

    # restoretime can't be empty
    with self.assertRaises(ActUserError) as excp:
      from datetime import datetime      
      act.clone_database(
        source_application=oracleapp[0], 
        restoretime=None,
        target_host=target_host_ora,
        strict_policy=True,
        ora_home=ora_home,
        ora_dbname=ora_dbname 
        )
    self.assertEqual(str(excp.exception), "Actifio User Error: 'restoretime' should be in the type of datetime or string with format of [YYYY-MM-DD HH:mm:ss]")

    # strict_policy 
    with self.assertRaises(ActUserError) as excp:
      from datetime import datetime      
      act.clone_database(
        source_application=oracleapp[0], 
        restoretime=datetime.today(),
        target_host=target_host_ora,
        strict_policy="none",
        ora_home=ora_home,
        ora_dbname=ora_dbname 
        )
    self.assertEqual(str(excp.exception), "Actifio User Error: 'strict_policy' should be boolean")

    # source_application need to be specified
    with self.assertRaises(ActUserError) as excp:
      from datetime import datetime      
      act.clone_database( 
        restoretime=datetime.today(),
        target_host=target_host_ora,
        strict_policy=True,
        ora_home=ora_home,
        ora_dbname=ora_dbname 
        )
    self.assertEqual(str(excp.exception), "Actifio User Error: 'source_application' or 'source_appname' and 'source_hostname' need to be specified.")

    # source_application need to be actApplication 
    with self.assertRaises(ActUserError) as excp:
      from datetime import datetime      
      act.clone_database(
        source_application="None", 
        restoretime=datetime.today(),
        target_host=target_host_ora,
        strict_policy=True,
        ora_home=ora_home,
        ora_dbname=ora_dbname 
        )
    self.assertEqual(str(excp.exception), "Actifio User Error: 'source_application' need to be ActApplication type.")

    # oracle params
    with self.assertRaises(ActUserError) as excp:
      from datetime import datetime      
      act.clone_database(
        source_application=oracleapp[0], 
        restoretime=datetime.today(),
        target_host=target_host_ora,
        strict_policy=True,
        oracle_db_name=ora_dbname 
        )
    self.assertEqual(str(excp.exception), "Actifio User Error: Required argument is missing: oracle_home")

    # oracle params
    with self.assertRaises(ActUserError) as excp:
      from datetime import datetime      
      act.clone_database(
        source_application=oracleapp[0], 
        restoretime=datetime.today(),
        target_host=target_host_ora,
        strict_policy=True,
        oracle_home=ora_home
        )
    self.assertEqual(str(excp.exception), "Actifio User Error: Required argument is missing: oracle_db_name")

    # sql params
    with self.assertRaises(ActUserError) as excp:
      from datetime import datetime      
      act.clone_database(
        source_application=sqldb[0], 
        restoretime=datetime.today(),
        target_host=target_host_ora,
        strict_policy=True,
        sql_instance_name=sql_dbinst
        )
    self.assertEqual(str(excp.exception), "Actifio User Error: Required argument is missing: sql_db_name")


if __name__ == "__main__":
  unittest.main()
