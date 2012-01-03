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

"""Regression test for core_helper.py

Make sure you are running this against a database that can be destroyed.

DO NOT EVER RUN THIS TEST AGAINST A PRODUCTION DATABASE.
"""


__copyright__ = 'Copyright (C) 2009, Purdue University'
__license__ = 'BSD'
__version__ = '#TRUNK#'


import datetime
import time
import unittest
import os

import roster_core
from roster_core import errors


CONFIG_FILE = 'test_data/roster.conf' # Example in test_data
SCHEMA_FILE = '../roster-core/data/database_schema.sql'
DATA_FILE = 'test_data/test_data.sql'
RECORDS_FILE = 'test_data/test_records.db'

class TestCoreHelpers(unittest.TestCase):

  def setUp(self):
    self.config_instance = roster_core.Config(file_name=CONFIG_FILE)

    db_instance = self.config_instance.GetDb()

    db_instance.CreateRosterDatabase()

    data = open(DATA_FILE, 'r').read()
    db_instance.StartTransaction()
    db_instance.cursor.execute(data)
    db_instance.EndTransaction()
    db_instance.close()

    self.unittest_timestamp = datetime.datetime.now().replace(microsecond=0)
    self.core_instance = roster_core.Core(u'sharrell', self.config_instance,
        unittest_timestamp=self.unittest_timestamp)
    self.core_helper_instance = roster_core.CoreHelpers(
        self.core_instance)

    self.core_instance.MakeView(u'test_view')
    self.core_instance.MakeView(u'test_view2')
    self.core_instance.MakeView(u'test_view3')
    self.core_instance.MakeZone(u'reverse_zone', u'master',
                                u'1.168.192.in-addr.arpa.',
                                view_name=u'test_view')
    self.core_instance.MakeZone(u'forward_zone', u'master',
                                u'university.edu.',
                                view_name=u'test_view')
    self.core_instance.MakeZone(u'forward_zone', u'master',
                                u'university.edu.',
                                view_name=u'test_view3')
    self.core_instance.MakeZone(u'reverse_zone', u'master',
                                u'1.168.192.in-addr.arpa.',
                                view_name=u'test_view2')
    self.core_instance.MakeZone(u'ipv6zone', u'master',
                                u'ipv6.net.', view_name=u'test_view')
    self.core_instance.MakeRecord(
        u'soa', u'soa1', u'ipv6zone',
        {u'name_server': u'ns1.university.edu.',
         u'admin_email': u'admin.university.edu.',
         u'serial_number': 1, u'refresh_seconds': 5,
         u'retry_seconds': 5, u'expiry_seconds': 5,
         u'minimum_seconds': 5}, view_name=u'test_view')
    self.core_instance.MakeRecord(
        u'soa', u'soa2', u'forward_zone',
        {u'name_server': u'ns1.university.edu.',
         u'admin_email': u'admin.university.edu.',
         u'serial_number': 1, u'refresh_seconds': 5,
         u'retry_seconds': 5, u'expiry_seconds': 5,
         u'minimum_seconds': 5}, view_name=u'test_view')
    self.core_instance.MakeRecord(
        u'soa', u'soa2', u'forward_zone',
        {u'name_server': u'ns1.university.edu.',
         u'admin_email': u'admin.university.edu.',
         u'serial_number': 1, u'refresh_seconds': 5,
         u'retry_seconds': 5, u'expiry_seconds': 5,
         u'minimum_seconds': 5}, view_name=u'test_view3')
    self.core_instance.MakeRecord(
        u'soa', u'soa2', u'reverse_zone',
        {u'name_server': u'ns1.university.edu.',
         u'admin_email': u'admin.university.edu.',
         u'serial_number': 1, u'refresh_seconds': 5,
         u'retry_seconds': 5, u'expiry_seconds': 5,
         u'minimum_seconds': 5}, view_name=u'test_view')
    self.core_instance.MakeRecord(
        u'soa', u'soa2', u'reverse_zone',
        {u'name_server': u'ns1.university.edu.',
         u'admin_email': u'admin.university.edu.',
         u'serial_number': 1, u'refresh_seconds': 5,
         u'retry_seconds': 5, u'expiry_seconds': 5,
         u'minimum_seconds': 5}, view_name=u'test_view2')
    self.core_instance.MakeRecord(
        u'aaaa', u'host2', u'ipv6zone', {u'assignment_ip':
            u'4321:0000:0001:0002:0003:0004:0567:89ab'}, view_name=u'test_view')
    self.core_instance.MakeRecord(
        u'aaaa', u'host2', u'ipv6zone', {u'assignment_ip':
            u'4321:0000:0001:0002:0003:0004:0567:89ac'}, view_name=u'test_view')
    self.core_instance.MakeRecord(
        u'aaaa', u'host2', u'ipv6zone', {u'assignment_ip':
            u'4321:0001:0001:0002:0003:0004:0567:89ab'}, view_name=u'test_view')
    self.core_instance.MakeRecord(
        u'aaaa', u'host2', u'ipv6zone', {u'assignment_ip':
            u'4321:0001:0001:0002:0003:0004:0567:89ac'}, view_name=u'test_view')
    self.core_instance.MakeRecord(u'a', u'host1', u'forward_zone',
                                  {u'assignment_ip': u'192.168.0.1'},
                                  view_name=u'test_view')
    self.core_instance.MakeRecord(u'a', u'host2', u'forward_zone',
                                  {u'assignment_ip': u'192.168.1.11'},
                                  view_name=u'test_view3')
    self.core_instance.MakeRecord(u'a', u'host3', u'forward_zone',
                                  {u'assignment_ip': u'192.168.1.5'},
                                  view_name=u'test_view3')
    self.core_instance.MakeRecord(u'a', u'host4', u'forward_zone',
                                  {u'assignment_ip': u'192.168.1.10'},
                                  view_name=u'test_view')
    self.core_instance.MakeRecord(u'a', u'host5', u'forward_zone',
                                  {u'assignment_ip': u'192.168.1.17'},
                                  view_name=u'test_view3')
    self.core_instance.MakeRecord(u'a', u'host6', u'forward_zone',
                                  {u'assignment_ip': u'192.168.1.8'},
                                  view_name=u'test_view')
    self.core_instance.MakeRecord(u'ptr', u'8',
                                  u'reverse_zone',
                                  {u'assignment_host':
                                      u'host6.university.edu.'},
                                  view_name=u'test_view')
    self.core_instance.MakeRecord(u'ptr', u'11',
                                  u'reverse_zone',
                                  {u'assignment_host':
                                      u'host2.university.edu.'},
                                  view_name=u'test_view2')
    self.core_instance.MakeRecord(u'ptr', u'5',
                                  u'reverse_zone',
                                  {u'assignment_host':
                                      u'host3.university.edu.'},
                                  view_name=u'test_view2')
    self.core_instance.MakeRecord(u'ptr', u'10',
                                  u'reverse_zone',
                                  {u'assignment_host':
                                      u'host4.university.edu.'},
                                  view_name=u'test_view2')
    self.core_instance.MakeRecord(u'ptr', u'7',
                                  u'reverse_zone',
                                  {u'assignment_host':
                                      u'host5.university.edu.'},
                                  view_name=u'test_view2')

  def testAddFormattedRecords(self):
    self.core_instance.MakeZone(u'records_zone', u'master',
                                u'records.edu.',
                                view_name=u'test_view3')
    self.assertEqual(
        self.core_instance.ListRecords(zone_name=u'records_zone'),
        [])
    self.core_instance.MakeRecord(
        u'soa', u'soa1', u'records_zone',
        {u'name_server': u'ns1.university.edu.',
         u'admin_email': u'admin.university.edu.',
         u'serial_number': 1, u'refresh_seconds': 5,
         u'retry_seconds': 5, u'expiry_seconds': 5,
         u'minimum_seconds': 5}, view_name=u'test_view3')

    records_file_string = 'university IN LOC 37 23 30.900 N 121 59 19.000 W 7.00m 100.00m 100.00m 2.00m'
    self.assertRaises(errors.UnexpectedDataError, self.core_helper_instance.AddFormattedRecords,
        u'records_zone', records_file_string, view=u'test_view3',
        use_soa=False)

    records_file_string = open(RECORDS_FILE, 'r').read()
    self.core_helper_instance.AddFormattedRecords(
        u'records_zone', records_file_string, view=u'test_view3',
        use_soa=False)
    self.assertEqual(
        self.core_instance.ListRecords(zone_name=u'records_zone'),
        [{u'serial_number': 3, u'refresh_seconds': 5,
          'target': u'soa1',
          u'name_server': u'ns1.university.edu.',
          u'retry_seconds': 5, 'ttl': 3600,
          u'minimum_seconds': 5, 'record_type': u'soa',
          'view_name': u'test_view3', 'last_user': u'sharrell',
          'zone_name': u'records_zone',
          u'admin_email': u'admin.university.edu.',
          u'expiry_seconds': 5},
         {'target': u'university.edu', u'weight': 5, 'ttl': 0,
          u'priority': 0, 'record_type': u'srv',
          'view_name': u'test_view3', 'last_user': u'sharrell',
          'zone_name': u'records_zone',
          u'assignment_host': u'test.sub.university.edu.',
          u'port': 80},
         {'target': u'desktop-1', 'ttl': 0, 'record_type': u'a',
          'view_name': u'test_view3', 'last_user': u'sharrell',
          'zone_name': u'records_zone',
          u'assignment_ip': u'192.168.1.100'},
         {'target': u'ns2', 'ttl': 0, 'record_type': u'a',
          'view_name': u'test_view3', 'last_user': u'sharrell',
          'zone_name': u'records_zone',
          u'assignment_ip': u'192.168.1.104'},
         {'target': u'www', 'ttl': 0, 'record_type': u'cname',
          'view_name': u'test_view3', 'last_user': u'sharrell',
          'zone_name': u'records_zone',
          u'assignment_host': u'sub.university.edu.'},
         {'target': u'ns', 'ttl': 0, 'record_type': u'a',
          'view_name': u'test_view3', 'last_user': u'sharrell',
          'zone_name': u'records_zone',
          u'assignment_ip': u'192.168.1.103'},
         {'target': u'www.data', 'ttl': 0,
          'record_type': u'cname', 'view_name': u'test_view3',
          'last_user': u'sharrell', 'zone_name': u'records_zone',
          u'assignment_host': u'ns.university.edu.'},
         {'target': u'mail1', 'ttl': 0, 'record_type': u'a',
          'view_name': u'test_view3', 'last_user': u'sharrell',
          'zone_name': u'records_zone',
          u'assignment_ip': u'192.168.1.101'},
         {'target': u'mail2', 'ttl': 0, 'record_type': u'a',
          'view_name': u'test_view3', 'last_user': u'sharrell',
          'zone_name': u'records_zone',
          u'assignment_ip': u'192.168.1.102'}])

  def testGetAssociatedCNAMEs(self):
    self.core_instance.MakeRecord(
        u'cname', u'cname_host2', u'forward_zone',
        {u'assignment_host': u'host2.university.edu.'},
        view_name=u'test_view3')
    self.core_instance.MakeRecord(
        u'cname', u'cname2_host2', u'forward_zone',
        {u'assignment_host': u'host2.university.edu.'},
        view_name=u'test_view3')
    self.core_instance.MakeRecord(
        u'cname', u'fry0', u'forward_zone',
        {u'assignment_host': u'host1.university.edu.'},
        view_name=u'test_view3')
    self.core_instance.MakeRecord(
        u'cname', u'bender', u'forward_zone',
        {u'assignment_host': u'host6.university.edu.'},
        view_name=u'test_view')
    self.core_instance.MakeRecord(
        u'cname', u'bender2', u'forward_zone',
        {u'assignment_host': u'bender.university.edu.'},
        view_name=u'test_view')
    self.assertEqual(self.core_helper_instance.GetAssociatedCNAMEs(
        u'host2.university.edu.', u'test_view3', u'forward_zone'),
        [{'target': u'cname_host2', 'ttl': 3600, 'record_type': u'cname',
          'view_name': u'test_view3', 'last_user': u'sharrell',
          'zone_name': u'forward_zone',
          'assignment_host': u'host2.university.edu.',
          'zone_origin': u'university.edu.'},
         {'target': u'cname2_host2', 'ttl': 3600, 'record_type': u'cname',
          'view_name': u'test_view3', 'last_user': u'sharrell',
          'zone_name': u'forward_zone',
          'assignment_host': u'host2.university.edu.',
          'zone_origin': u'university.edu.'}])
    self.assertEqual(self.core_helper_instance.GetAssociatedCNAMEs(
        u'host6.university.edu.', u'test_view3', u'forward_zone'),
        [])
    self.assertEqual(self.core_helper_instance.GetAssociatedCNAMEs(
        u'unknownhost.university.edu.', u'test_view3', u'forward_zone'),
        [])
    self.assertEqual(self.core_helper_instance.GetAssociatedCNAMEs(
        u'host6.university.edu.', u'test_view', u'forward_zone'),
        [{'target': u'bender', 'ttl': 3600, 'record_type': u'cname',
          'view_name': u'test_view', 'last_user': u'sharrell',
          'zone_name': u'forward_zone',
          'assignment_host': u'host6.university.edu.',
          'zone_origin': u'university.edu.'}])
    self.assertEqual(self.core_helper_instance.GetAssociatedCNAMEs(
        u'host6.university.edu.', u'test_view', u'forward_zone',
        recursive=True),
        [{'target': u'bender', 'ttl': 3600, 'record_type': u'cname',
          'view_name': u'test_view', 'last_user': u'sharrell',
          'zone_name': u'forward_zone',
          'assignment_host': u'host6.university.edu.',
          'zone_origin': u'university.edu.'},
         {'target': u'bender2', 'ttl': 3600, 'record_type': u'cname',
          'view_name': u'test_view', 'last_user': u'sharrell',
          'zone_name': u'forward_zone',
          'assignment_host': u'bender.university.edu.',
          'zone_origin': u'university.edu.'}])
    # 100 CNAMEs pointing to the same host
    for i in range(100):
      self.core_instance.MakeRecord(
          u'cname', u'loop%d' % i, u'forward_zone',
          {u'assignment_host': u'host6.university.edu.'},
          view_name=u'test_view')
    self.assertEqual(len(self.core_helper_instance.GetAssociatedCNAMEs(
        u'host6.university.edu.', u'test_view', u'forward_zone')), 101)
    # 100 CNAMEs recursively pointing to each other pointing to one host
    for i in range(100):
      self.core_instance.MakeRecord(
          u'cname', u'fry%d' % (i + 1), u'forward_zone',
          {u'assignment_host': u'fry%d.university.edu.' % i},
          view_name=u'test_view3')
    self.assertEqual(len(self.core_helper_instance.GetAssociatedCNAMEs(
        u'host1.university.edu.', u'test_view3', u'forward_zone',
        recursive=True)), 101)

  def testListRecordByIPAddress(self):
    self.core_instance.MakeReverseRangeZoneAssignment(u'reverse_zone',
                                                      u'192.168.1.0/24')
    self.assertEqual(self.core_helper_instance.ListRecordsByCIDRBlock(
      u'192.168.1.17', view_name=u'test_view3'),
      {u'test_view3': {u'192.168.1.17':
          [{'record_ttl': 3600,
          'record_last_user': u'sharrell',
          u'host': u'host5.university.edu',
          u'forward': True,
          'record_type': u'a',
          u'view_name': u'test_view3',
          'records_id': 14,
          u'record_args_dict': {'assignment_ip': u'192.168.1.17'},
          'record_target': u'host5',
          'record_zone_name': u'forward_zone',
          u'zone_origin': u'university.edu.',
          'record_view_dependency': u'test_view3_dep'}]}})
    self.assertEqual(self.core_helper_instance.ListRecordsByCIDRBlock(
        u'192.168.1.7', view_name=u'test_view2'),
        {u'test_view2': {u'192.168.1.7':
            [{'record_ttl': 3600,
            'record_last_user': u'sharrell',
            u'host': u'host5.university.edu',
            u'forward': False,
            'record_type': u'ptr',
            u'view_name': u'test_view2',
            'records_id': 20,
            u'record_args_dict': {'assignment_ip': u'192.168.1.7'},
            'record_target': u'7',
            'record_zone_name': u'reverse_zone',
            u'zone_origin': u'1.168.192.in-addr.arpa.',
            'record_view_dependency': u'test_view2_dep'}]}})

    returned_dict = self.core_helper_instance.ListRecordsByCIDRBlock(
        u'4321:0000:0001:0002:0003:0004:0567:89ab', view_name=u'test_view')
    self.assertEqual(len(returned_dict), 1)
    self.assertEqual(len(returned_dict[u'test_view']), 1)
    self.assertEqual(len(
        returned_dict[u'test_view'][u'4321:0000:0001:0002:0003:0004:0567:89ab']), 1)
    self.assertTrue(
        { u'forward': True,
          u'host': u'host2.ipv6.net',
          u'record_args_dict': { 'assignment_ip': u'4321:0000:0001:0002:0003:0004:0567:89ab'},
          'record_last_user': u'sharrell',
          'record_target': u'host2',
          'record_ttl': 3600,
          'record_type': u'aaaa',
          'record_view_dependency': u'test_view_dep',
          'record_zone_name': u'ipv6zone',
          'records_id': 6,
          u'view_name': u'test_view',
          u'zone_origin': u'ipv6.net.'} in
        returned_dict[u'test_view'][u'4321:0000:0001:0002:0003:0004:0567:89ab'])

    returned_dict = self.core_helper_instance.ListRecordsByCIDRBlock(
      u'192.168.1.8', view_name=u'test_view')
    self.assertEqual(len(returned_dict), 1)
    self.assertEqual(len(returned_dict[u'test_view']), 1)
    self.assertEqual(len(returned_dict[u'test_view'][u'192.168.1.8']), 2)
    self.assertTrue(
        { u'forward': False,
          u'host': u'host6.university.edu',
          u'record_args_dict': { 'assignment_ip': u'192.168.1.8'},
          'record_last_user': u'sharrell',
          'record_target': u'8',
          'record_ttl': 3600,
          'record_type': u'ptr',
          'record_view_dependency': u'test_view_dep',
          'record_zone_name': u'reverse_zone',
          'records_id': 16,
          u'view_name': u'test_view',
          u'zone_origin': u'1.168.192.in-addr.arpa.'} in
        returned_dict[u'test_view'][u'192.168.1.8'])
    self.assertTrue(
        { u'forward': True,
          u'host': u'host6.university.edu',
          u'record_args_dict': { 'assignment_ip': u'192.168.1.8'},
          'record_last_user': u'sharrell',
          'record_target': u'host6',
          'record_ttl': 3600,
          'record_type': u'a',
          'record_view_dependency': u'test_view_dep',
          'record_zone_name': u'forward_zone',
          'records_id': 15,
          u'view_name': u'test_view',
          u'zone_origin': u'university.edu.'} in
        returned_dict[u'test_view'][u'192.168.1.8'])

  def testListRecordsByCIDRBlock(self):
    self.core_instance.MakeReverseRangeZoneAssignment(u'reverse_zone',
                                                      u'192.168.1.0/24')

    returned_dict = self.core_helper_instance.ListRecordsByCIDRBlock(
        u'192.168.1.4/30')
    self.assertTrue(len(returned_dict), 2)
    self.assertTrue(len(returned_dict[u'test_view2']), 2)
    self.assertTrue(len(returned_dict[u'test_view3']), 1)
    self.assertTrue(len(returned_dict[u'test_view2'][u'192.168.1.7']), 1)
    self.assertTrue(len(returned_dict[u'test_view2'][u'192.168.1.5']), 1)
    self.assertTrue(len(returned_dict[u'test_view3'][u'192.168.1.5']), 1)
    self.assertTrue(
        { u'forward': False,
          u'host': u'host5.university.edu',
          u'record_args_dict': { 'assignment_ip': u'192.168.1.7'},
          'record_last_user': u'sharrell',
          'record_target': u'7',
          'record_ttl': 3600,
          'record_type': u'ptr',
          'record_view_dependency': u'test_view2_dep',
          'record_zone_name': u'reverse_zone',
          'records_id': 20,
          u'view_name': u'test_view2',
          u'zone_origin': u'1.168.192.in-addr.arpa.'} in
        returned_dict[u'test_view2'][u'192.168.1.7'])
    self.assertTrue(
        { u'forward': False,
          u'host': u'host3.university.edu',
          u'record_args_dict': { 'assignment_ip': u'192.168.1.5'},
          'record_last_user': u'sharrell',
          'record_target': u'5',
          'record_ttl': 3600,
          'record_type': u'ptr',
          'record_view_dependency': u'test_view2_dep',
          'record_zone_name': u'reverse_zone',
          'records_id': 18,
          u'view_name': u'test_view2',
          u'zone_origin': u'1.168.192.in-addr.arpa.'} in
        returned_dict[u'test_view2'][u'192.168.1.5'])
    self.assertTrue(
        { u'forward': True,
          u'host': u'host3.university.edu',
          u'record_args_dict': { 'assignment_ip': u'192.168.1.5'},
          'record_last_user': u'sharrell',
          'record_target': u'host3',
          'record_ttl': 3600,
          'record_type': u'a',
          'record_view_dependency': u'test_view3_dep',
          'record_zone_name': u'forward_zone',
          'records_id': 12,
          u'view_name': u'test_view3',
          u'zone_origin': u'university.edu.'} in
        returned_dict[u'test_view3'][u'192.168.1.5'])

    returned_dict = self.core_helper_instance.ListRecordsByCIDRBlock(
        u'4321:0000:0001:0002:0003:0004:0567:8900/120', view_name=u'test_view')
    self.assertEqual(len(returned_dict), 1)
    self.assertEqual(len(returned_dict[u'test_view']), 2)
    self.assertEqual(len(
        returned_dict[u'test_view'][u'4321:0000:0001:0002:0003:0004:0567:89ab']), 1)
    self.assertEqual(len(
        returned_dict[u'test_view'][u'4321:0000:0001:0002:0003:0004:0567:89ac']), 1)
    self.assertTrue(
        { u'forward': True,
          u'host': u'host2.ipv6.net',
          u'record_args_dict': { 'assignment_ip': u'4321:0000:0001:0002:0003:0004:0567:89ab'},
          'record_last_user': u'sharrell',
          'record_target': u'host2',
          'record_ttl': 3600,
          'record_type': u'aaaa',
          'record_view_dependency': u'test_view_dep',
          'record_zone_name': u'ipv6zone',
          'records_id': 6,
          u'view_name': u'test_view',
          u'zone_origin': u'ipv6.net.'} in
        returned_dict[u'test_view'][u'4321:0000:0001:0002:0003:0004:0567:89ab'])
    self.assertTrue(
        { u'forward': True,
          u'host': u'host2.ipv6.net',
          u'record_args_dict': { 'assignment_ip': u'4321:0000:0001:0002:0003:0004:0567:89ac'},
          'record_last_user': u'sharrell',
          'record_target': u'host2',
          'record_ttl': 3600,
          'record_type': u'aaaa',
          'record_view_dependency': u'test_view_dep',
          'record_zone_name': u'ipv6zone',
          'records_id': 7,
          u'view_name': u'test_view',
          u'zone_origin': u'ipv6.net.'} in
        returned_dict[u'test_view'][u'4321:0000:0001:0002:0003:0004:0567:89ac'])

    returned_dict = self.core_helper_instance.ListRecordsByCIDRBlock(
        u'4321:0001:0000:0000:0000:0000:0000:0000/32', view_name=u'test_view')
    self.assertEqual(len(returned_dict), 1)
    self.assertEqual(len(returned_dict[u'test_view']), 2)
    self.assertEqual(len(
        returned_dict[u'test_view'][u'4321:0001:0001:0002:0003:0004:0567:89ab']), 1)
    self.assertEqual(len(
        returned_dict[u'test_view'][u'4321:0001:0001:0002:0003:0004:0567:89ac']), 1)
    self.assertTrue(
        { u'forward': True,
          u'host': u'host2.ipv6.net',
          u'record_args_dict': { 'assignment_ip': u'4321:0001:0001:0002:0003:0004:0567:89ab'},
          'record_last_user': u'sharrell',
          'record_target': u'host2',
          'record_ttl': 3600,
          'record_type': u'aaaa',
          'record_view_dependency': u'test_view_dep',
          'record_zone_name': u'ipv6zone',
          'records_id': 8,
          u'view_name': u'test_view',
          u'zone_origin': u'ipv6.net.'} in
        returned_dict[u'test_view'][u'4321:0001:0001:0002:0003:0004:0567:89ab'])
    self.assertTrue(
        { u'forward': True,
          u'host': u'host2.ipv6.net',
          u'record_args_dict': { 'assignment_ip': u'4321:0001:0001:0002:0003:0004:0567:89ac'},
          'record_last_user': u'sharrell',
          'record_target': u'host2',
          'record_ttl': 3600,
          'record_type': u'aaaa',
          'record_view_dependency': u'test_view_dep',
          'record_zone_name': u'ipv6zone',
          'records_id': 9,
          u'view_name': u'test_view',
          u'zone_origin': u'ipv6.net.'} in
        returned_dict[u'test_view'][u'4321:0001:0001:0002:0003:0004:0567:89ac'])

    returned_dict = self.core_helper_instance.ListRecordsByCIDRBlock(
        u'::/0', view_name=u'test_view')
    self.assertEqual(len(returned_dict), 1)
    self.assertEqual(len(
        returned_dict[u'test_view'][u'4321:0000:0001:0002:0003:0004:0567:89ab']), 1)
    self.assertEqual(len(
        returned_dict[u'test_view'][u'4321:0000:0001:0002:0003:0004:0567:89ac']), 1)
    self.assertEqual(len(returned_dict[u'test_view']), 4)
    self.assertEqual(len(
        returned_dict[u'test_view'][u'4321:0001:0001:0002:0003:0004:0567:89ab']), 1)
    self.assertEqual(len(
        returned_dict[u'test_view'][u'4321:0001:0001:0002:0003:0004:0567:89ac']), 1)
    self.assertTrue(
        { u'forward': True,
          u'host': u'host2.ipv6.net',
          u'record_args_dict': { 'assignment_ip': u'4321:0000:0001:0002:0003:0004:0567:89ab'},
          'record_last_user': u'sharrell',
          'record_target': u'host2',
          'record_ttl': 3600,
          'record_type': u'aaaa',
          'record_view_dependency': u'test_view_dep',
          'record_zone_name': u'ipv6zone',
          'records_id': 6,
          u'view_name': u'test_view',
          u'zone_origin': u'ipv6.net.'} in
        returned_dict[u'test_view'][u'4321:0000:0001:0002:0003:0004:0567:89ab'])
    self.assertTrue(
        { u'forward': True,
          u'host': u'host2.ipv6.net',
          u'record_args_dict': { 'assignment_ip': u'4321:0000:0001:0002:0003:0004:0567:89ac'},
          'record_last_user': u'sharrell',
          'record_target': u'host2',
          'record_ttl': 3600,
          'record_type': u'aaaa',
          'record_view_dependency': u'test_view_dep',
          'record_zone_name': u'ipv6zone',
          'records_id': 7,
          u'view_name': u'test_view',
          u'zone_origin': u'ipv6.net.'} in
        returned_dict[u'test_view'][u'4321:0000:0001:0002:0003:0004:0567:89ac'])
    self.assertTrue(
        { u'forward': True,
          u'host': u'host2.ipv6.net',
          u'record_args_dict': { 'assignment_ip': u'4321:0001:0001:0002:0003:0004:0567:89ab'},
          'record_last_user': u'sharrell',
          'record_target': u'host2',
          'record_ttl': 3600,
          'record_type': u'aaaa',
          'record_view_dependency': u'test_view_dep',
          'record_zone_name': u'ipv6zone',
          'records_id': 8,
          u'view_name': u'test_view',
          u'zone_origin': u'ipv6.net.'} in
        returned_dict[u'test_view'][u'4321:0001:0001:0002:0003:0004:0567:89ab'])
    self.assertTrue(
        { u'forward': True,
          u'host': u'host2.ipv6.net',
          u'record_args_dict': { 'assignment_ip': u'4321:0001:0001:0002:0003:0004:0567:89ac'},
          'record_last_user': u'sharrell',
          'record_target': u'host2',
          'record_ttl': 3600,
          'record_type': u'aaaa',
          'record_view_dependency': u'test_view_dep',
          'record_zone_name': u'ipv6zone',
          'records_id': 9,
          u'view_name': u'test_view',
          u'zone_origin': u'ipv6.net.'} in
        returned_dict[u'test_view'][u'4321:0001:0001:0002:0003:0004:0567:89ac'])

    self.assertRaises(errors.InvalidInputError,
        self.core_helper_instance.ListRecordsByCIDRBlock, 'invalid ip')
    self.assertRaises(errors.InvalidInputError,
        self.core_helper_instance.ListRecordsByCIDRBlock, '12345::/112')
    self.assertRaises(errors.InvalidInputError,
        self.core_helper_instance.ListRecordsByCIDRBlock, '192.168.0.256')
    self.assertRaises(errors.InvalidInputError,
        self.core_helper_instance.ListRecordsByCIDRBlock, '192.168.0.1/33')
    self.assertRaises(errors.InvalidInputError,
        self.core_helper_instance.ListRecordsByCIDRBlock, '4321:1:2:3:4:567:89ac/129')
    self.assertRaises(errors.InvalidInputError,
        self.core_helper_instance.ListRecordsByCIDRBlock, '4321:1:2:3:4:567:89ac/112')
    self.assertRaises(errors.InvalidInputError,
        self.core_helper_instance.ListRecordsByCIDRBlock, '0.0.0.0/-1')
    self.assertRaises(errors.InvalidInputError,
        self.core_helper_instance.ListRecordsByCIDRBlock, '')

  def testListAvailableIpsInCIDR(self):
    self.core_instance.MakeReverseRangeZoneAssignment(u'reverse_zone',
                                                      u'192.168.1.0/24')
    self.assertEqual(self.core_helper_instance.ListAvailableIpsInCIDR(
        '192.168.1.4/30', num_ips=3), ['192.168.1.6'])
    self.assertEqual(self.core_helper_instance.ListAvailableIpsInCIDR(
        '192.168.0.0/29', num_ips=4), ['192.168.0.2', '192.168.0.3',
                                       '192.168.0.4', '192.168.0.5'])
    self.assertRaises(errors.CoreError,
         self.core_helper_instance.ListAvailableIpsInCIDR,
        '240.0.0.0/24', num_ips=10)
    self.assertEqual(self.core_helper_instance.ListAvailableIpsInCIDR(
        '2001:0400::/64', num_ips=10),
        ['2001:0400:0000:0000:0000:0000:0000:0001',
         '2001:0400:0000:0000:0000:0000:0000:0002',
         '2001:0400:0000:0000:0000:0000:0000:0003',
         '2001:0400:0000:0000:0000:0000:0000:0004',
         '2001:0400:0000:0000:0000:0000:0000:0005',
         '2001:0400:0000:0000:0000:0000:0000:0006',
         '2001:0400:0000:0000:0000:0000:0000:0007',
         '2001:0400:0000:0000:0000:0000:0000:0008',
         '2001:0400:0000:0000:0000:0000:0000:0009',
         '2001:0400:0000:0000:0000:0000:0000:000a'])
    self.assertRaises(errors.CoreError,
         self.core_helper_instance.ListAvailableIpsInCIDR,
        '4::/64', num_ips=10)
    self.assertEqual(self.core_helper_instance.ListAvailableIpsInCIDR(
        '2001:0400::/123', num_ips=10),
        ['2001:0400:0000:0000:0000:0000:0000:0001',
         '2001:0400:0000:0000:0000:0000:0000:0002',
         '2001:0400:0000:0000:0000:0000:0000:0003',
         '2001:0400:0000:0000:0000:0000:0000:0004',
         '2001:0400:0000:0000:0000:0000:0000:0005',
         '2001:0400:0000:0000:0000:0000:0000:0006',
         '2001:0400:0000:0000:0000:0000:0000:0007',
         '2001:0400:0000:0000:0000:0000:0000:0008',
         '2001:0400:0000:0000:0000:0000:0000:0009',
         '2001:0400:0000:0000:0000:0000:0000:000a'])

  def testUnReverseIP(self):
    self.assertEqual(self.core_helper_instance.UnReverseIP(
        'b.a.9.8.7.6.5.0.4.0.0.0.3.0.0.0.2.0.0.0.1.0.0.0.0.0.0.0.1.2.3.4.'
        'ip6.arpa.'), '4321:0000:0001:0002:0003:0004:0567:89ab')
    self.assertEqual(self.core_helper_instance.UnReverseIP(
        '4.1.168.192.in-addr.arpa.'), '192.168.1.4')
    self.assertEqual(self.core_helper_instance.UnReverseIP(
        '64/27.23.168.192.in-addr.arpa.'), '192.168.23.64/27')
    self.assertEqual(self.core_helper_instance.UnReverseIP(
        '0.168.192.in-addr.arpa.'), '192.168.0/24')
    self.assertEqual(self.core_helper_instance.UnReverseIP(
        '168.192.in-addr.arpa.'), '192.168/16')

  def testReverseIP(self):
    self.assertEqual(self.core_helper_instance.ReverseIP(
        u'192.168.0/26'), u'0/26.168.192.in-addr.arpa.')
    self.assertEqual(self.core_helper_instance.ReverseIP(
        u'192.168.0/31'), u'0/31.168.192.in-addr.arpa.')

  def testListAccessRights(self):
    self.assertEqual(self.core_helper_instance.ListAccessRights(), ['rw', 'r'])

  def testRevertNamedConfig(self):
    self.core_instance.MakeDnsServerSet(u'set1')
    self.core_instance.MakeNamedConfGlobalOption(u'set1', u'test_options;')
    self.core_instance.MakeNamedConfGlobalOption(u'set1', u'test_options2;')
    self.assertEqual(self.core_instance.ListNamedConfGlobalOptions(),
                     [{'timestamp': self.unittest_timestamp,
                       'options': u'test_options;', 'id': 1,
                       'dns_server_set_name': u'set1'},
                      {'timestamp': self.unittest_timestamp,
                       'options': u'test_options2;', 'id': 2,
                       'dns_server_set_name': u'set1'}])
    self.core_helper_instance.RevertNamedConfig(u'set1', 1)
    self.assertEqual(self.core_instance.ListNamedConfGlobalOptions(),
                     [{'timestamp': self.unittest_timestamp,
                       'options': u'test_options;', 'id': 1,
                       'dns_server_set_name': u'set1'},
                      {'timestamp': self.unittest_timestamp,
                       'options': u'test_options2;', 'id': 2,
                       'dns_server_set_name': u'set1'},
                      {'timestamp': self.unittest_timestamp,
                       'options': u'test_options;', 'id': 3,
                       'dns_server_set_name': u'set1'}])
    config_dict = self.core_instance.db_instance.GetEmptyRowDict(
        'named_conf_global_options')
    config_dict['named_conf_global_options_id'] = 3
    update_config_dict = self.core_instance.db_instance.GetEmptyRowDict(
        'named_conf_global_options')
    time_difference = self.unittest_timestamp + datetime.timedelta(seconds=1)
    update_config_dict['options_created'] = time_difference
    self.core_instance.db_instance.StartTransaction()
    try:
      self.core_instance.db_instance.UpdateRow('named_conf_global_options',
                                               config_dict, update_config_dict)
    except:
      self.core_instance.db_instance.EndTransaction(rollback=True)
      raise
    self.core_instance.db_instance.EndTransaction()
    time.sleep(2)
    self.assertEqual(self.core_helper_instance.ListLatestNamedConfig(u'set1'),
        {'timestamp': time_difference, 
        'options': u'test_options;', 'id': 3, 'dns_server_set_name': u'set1'})

  def testListZoneByIPAddress(self):
    self.core_instance.MakeReverseRangeZoneAssignment(u'forward_zone',
                                                      u'192.168.1.0/24')
    self.assertEqual(
        self.core_helper_instance.ListZoneByIPAddress(u'192.168.1.1'),
        u'forward_zone')

  def testRemoveCNamesByAssignmentHost(self):
    self.assertEqual(self.core_instance.ListRecords(record_type=u'cname'), [])
    self.core_instance.MakeRecord(
        u'cname', u'cname_host2', u'forward_zone',
        {u'assignment_host': u'host2.university.edu.'},
        view_name=u'test_view3')
    self.core_instance.MakeRecord(
        u'cname', u'cname2_host2', u'forward_zone',
        {u'assignment_host': u'host2.university.edu.'},
        view_name=u'test_view3')
    self.core_instance.MakeRecord(
        u'cname', u'cname3_host2', u'forward_zone',
        {u'assignment_host': u'host1.university.edu.'},
        view_name=u'test_view3')
    self.assertEqual(self.core_instance.ListRecords(record_type=u'cname'),
                     [{'target': u'cname_host2', 'ttl': 3600,
                       'record_type': u'cname', 'view_name': u'test_view3',
                       'last_user': u'sharrell', 'zone_name': u'forward_zone',
                       u'assignment_host': u'host2.university.edu.'},
                      {'target': u'cname2_host2', 'ttl': 3600,
                       'record_type': u'cname', 'view_name': u'test_view3',
                       'last_user': u'sharrell', 'zone_name': u'forward_zone',
                       u'assignment_host': u'host2.university.edu.'},
                      {'target': u'cname3_host2', 'ttl': 3600,
                       'record_type': u'cname', 'view_name': u'test_view3',
                       'last_user': u'sharrell', 'zone_name': u'forward_zone',
                       u'assignment_host': u'host1.university.edu.'}])
    self.core_helper_instance.RemoveCNamesByAssignmentHost(
        u'host2.university.edu.', u'test_view3', u'forward_zone')
    self.assertEqual(self.core_instance.ListRecords(record_type=u'cname'),
                     [{'target': u'cname3_host2', 'ttl': 3600,
                       'record_type': u'cname', 'view_name': u'test_view3',
                       'last_user': u'sharrell', 'zone_name': u'forward_zone',
                       u'assignment_host': u'host1.university.edu.'}])

  def testProcessRecordsBatch(self):
    self.assertEqual(
        self.core_instance.ListRecords(record_type=u'a', target=u'host1'),
        [{'target': u'host1', 'ttl': 3600, 'record_type': u'a',
          'view_name': u'test_view', 'last_user': u'sharrell',
          'zone_name': u'forward_zone', u'assignment_ip': u'192.168.0.1'}])
    self.assertEqual(
        self.core_helper_instance.ProcessRecordsBatch(delete_records=[{
            'record_type': u'a', u'record_target': u'host1', 'records_id': 10,
            'record_zone_name': u'forward_zone', 'record_last_user': u'sharrell',
            u'record_view_dependency': u'test_view_dep', 'record_ttl': 3600}],
            add_records=[{'record_type': u'a', 'record_target': u'blah',
                          'record_zone_name': u'forward_zone',
                          u'record_view_dependency': u'test_view', 'record_arguments':
                              {u'assignment_ip': u'192.168.0.88'}}]), 2)
    self.assertEqual(
        self.core_instance.ListRecords(record_type=u'a', target=u'host1'), [])
    self.assertEqual(
        self.core_instance.ListRecords(record_type=u'a', target=u'blah'),
        [{'target': u'blah', 'ttl': 3600, 'record_type': u'a',
          'view_name': u'test_view', 'last_user': u'sharrell',
          'zone_name': u'forward_zone', u'assignment_ip': u'192.168.0.88'}])
    self.assertRaises(errors.RecordsBatchError,
        self.core_helper_instance.ProcessRecordsBatch, add_records=[{
            'record_target': u'blah', 'ttl': 3600, 'record_type': u'a',
            'record_view_dependency': u'test_view',
            'last_user': u'sharrell',
            'record_zone_name': u'forward_zone',
            'record_arguments': {u'assignment_ip': u'192.168.0.88'}}])
    self.assertRaises(errors.RecordsBatchError,
        self.core_helper_instance.ProcessRecordsBatch, add_records=[
            {'record_type': u'aaaa', 'record_target': u'host2',
             'record_zone_name': u'ipv6zone',
             'record_arguments': {u'assignment_ip':
                 u'4321:0000:0001:0002:0003:0004:0567:89ab'},
             'record_view_dependency': u'test_view'}])
    self.core_instance.MakeRecord(
        u'cname', u'university_edu', u'forward_zone',
        {u'assignment_host': u'blah.university.edu.'}, view_name=u'test_view')
    self.assertRaises(errors.RecordsBatchError,
        self.core_helper_instance.ProcessRecordsBatch, add_records=[
          {'record_type': u'a', 'record_target': u'university_edu',
            'record_zone_name': u'forward_zone',
            'record_arguments': {u'assignment_ip': u'192.168.1.1'},
          'record_view_dependency': u'test_view'}])
    self.assertRaises(errors.RecordsBatchError,
        self.core_helper_instance.ProcessRecordsBatch, add_records=[
            {'record_type': u'cname', 'record_target': u'blah',
             'record_zone_name': u'forward_zone',
             u'record_view_dependency': u'test_view', 'record_arguments':
                 {u'assignment_host': u'hostname.'}}])

if( __name__ == '__main__' ):
      unittest.main()
