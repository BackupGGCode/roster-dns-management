#!/usr/bin/python

# Copyright (c) 2009, Purdue University
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
# 
# Neither the name of the Purdue University nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""Test for Credential cache library."""

__copyright__ = 'Copyright (C) 2009, Purdue University'
__license__ = 'BSD'
__version__ = '#TRUNK#'


import datetime
import time
import unittest


import roster_core
import roster_server

import fakeldap

CONFIG_FILE = os.path.expanduser('~/.rosterrc') # Example in test_data
SCHEMA_FILE = '../roster-core/data/database_schema.sql'
DATA_FILE = 'test_data/test_data.sql'
HOST = u'localhost'
USERNAME = u'sharrell'
KEYFILE=('test_data/dnsmgmt.key.pem')
CERTFILE=('test_data/dnsmgmt.cert.pem')
CREDFILE='test_data/dnscred'


class TestCredentialsLibrary(unittest.TestCase):

  def setUp(self):
    self.config_instance = roster_core.Config(file_name=CONFIG_FILE)
    db_instance = self.config_instance.GetDb()

    schema = open(SCHEMA_FILE, 'r').read()
    db_instance.StartTransaction()
    db_instance.cursor.execute(schema)
    db_instance.CommitTransaction()

    data = open(DATA_FILE, 'r').read()
    db_instance.StartTransaction()
    db_instance.cursor.execute(data)
    db_instance.CommitTransaction()
    db_instance.close()

    self.server_instance = roster_server.Server(self.config_instance, KEYFILE,
                                                CERTFILE, core_die_time=5,
                                                inf_renew_time=5, clean_time=0,
                                                ldap_module=fakeldap)
    self.credential = self.server_instance.GetCredentials(USERNAME, u'test')
    self.server_instance.core_store = [] # Clear out core instance from above

  def testCoreRun(self):
    new_cred = self.server_instance.GetCredentials(u'shuey', 'testpass')
    self.assertEqual(self.server_instance.CoreRun('ListUsers', USERNAME,
                                                  self.credential),
                     {'new_credential': u'',
                      'core_return': {u'shuey': 64, u'jcollins': 32,
                                      u'sharrell': 128}})
    self.assertEqual(self.server_instance.CoreRun('ListUsers', USERNAME,
                                                  self.credential),
                     {'new_credential': u'',
                      'core_return': {u'shuey': 64, u'jcollins': 32,
                                      u'sharrell': 128}})
    self.assertTrue(len(self.server_instance.core_store))
    time.sleep(6)
    self.server_instance.CleanupCoreStore()
    self.assertFalse(len(self.server_instance.core_store))
    self.assertEqual(self.server_instance.CoreRun('ListUsers', USERNAME,
                                                  self.credential),
                     {'new_credential': u'',
                      'core_return': {u'shuey': 64, u'jcollins': 32,
                                      u'sharrell': 128}})
    self.assertEqual(self.server_instance.CoreRun('ListUsers', USERNAME,
                                                  self.credential),
                     {'new_credential': u'',
                      'core_return': {u'shuey': 64, u'jcollins': 32,
                                      u'sharrell': 128}})
    self.assertEqual(self.server_instance.CoreRun('ListUsers', u'shuey',
                                                  self.credential),
                     {'new_credential': u'',
                      'core_return': {u'shuey': 64, u'jcollins': 32,
                                      u'sharrell': 128}})
    self.assertEqual(len(self.server_instance.core_store), 2)

  def testCoreStoreCleanup(self):
    self.assertEqual(self.server_instance.core_store, [])
    self.assertEqual(self.server_instance.CoreRun(u'ListUsers', USERNAME,
                                        self.credential)['core_return'],
                     {'shuey': 64, 'jcollins': 32, 'sharrell': 128})
    self.assertTrue(len(self.server_instance.core_store))
    time.sleep(6)
    self.assertEqual(self.server_instance.CoreRun(u'ListUsers', USERNAME,
                                        self.credential)['core_return'],
                     {'shuey': 64, 'jcollins': 32, 'sharrell': 128})
    self.server_instance.CleanupCoreStore()
    self.assertFalse(len(self.server_instance.core_store))

  def testCoreWrongPassword(self):
    initial_time = datetime.datetime.now()
    self.server_instance.GetCredentials(u'shuey', u'fakepass')
    self.server_instance.GetCredentials(u'shuey', u'fakepass')
    self.server_instance.GetCredentials(u'shuey', u'fakepass')
    self.server_instance.GetCredentials(u'shuey', u'fakepass')
    self.assertTrue( initial_time + datetime.timedelta(seconds=4) < (
        datetime.datetime.now()))

  def testStringToUnicode(self):
    self.assertEqual(repr(self.server_instance.StringToUnicode('test')),
                     "u'test'")
    self.assertEqual(self.server_instance.StringToUnicode(2), 2)
                    
    self.assertEqual(repr(self.server_instance.StringToUnicode(
        [{'record_target': 'host3', 'record_type': 'a',
          'view_name': 'test_view', 'record_zone_name': 'forward_zone',
          'record_arguments': {'assignment_ip': '192.168.1.5'}},
         {'record_target': '5', 'record_type': 'ptr',
          'view_name': 'test_view', 'record_zone_name': 'forward_zone',
          'record_arguments': {'assignment_host': 'host3.university.edu.'}}])),
        "[{u'record_target': u'host3', u'record_type': u'a', "
          "u'view_name': u'test_view', u'record_zone_name': u'forward_zone', "
          "u'record_arguments': {u'assignment_ip': u'192.168.1.5'}}, "
         "{u'record_target': u'5', u'record_type': u'ptr', "
          "u'view_name': u'test_view', u'record_zone_name': u'forward_zone', "
          "u'record_arguments': {u'assignment_host': u'host3.university.edu.'}}]")

if( __name__ == '__main__' ):
  unittest.main()

