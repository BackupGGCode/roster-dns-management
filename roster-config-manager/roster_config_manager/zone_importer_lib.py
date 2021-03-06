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

"""This module contains all of the logic for the zone importer.

It should be only called by the importer.
"""

__copyright__ = 'Copyright (C) 2009, Purdue University'
__license__ = 'BSD'
__version__ = '#TRUNK#'

import os

import dns.zone
import IPy
import roster_core
from roster_core import errors


roster_core.core.CheckCoreVersionMatches(__version__)


class Error(Exception):
  pass

class IncludeError(Error):
  pass

class ZoneImport(object):
  """This class will only import one zone per init. It will load the zone
  from a file using dns.zone and then use the core API to put it in
  the database.
  """
  def __init__(self, zone_file_name, config_file_name, user_name, view,
               zone_name):
    """Sets self.core_instance, self.zone self.domain and self.view.

    Inputs:
      zone_file_name: name of zone file to import
      config_file_name: name of config file to load db info from
      user_name: username of person running the script
      view: name of view to import records to
      zone_name: name of the zone to import records to
    """
    config_instance = roster_core.Config(file_name=config_file_name)

    self.core_instance = roster_core.Core(user_name, config_instance)
    self.core_helper_instance = roster_core.CoreHelpers(
        self.core_instance)

    zone_file_dir = os.path.dirname(zone_file_name)
    zone_lines = []
    zone_file = open(zone_file_name, 'r')
    try:
      for line in zone_file:
        if( line.startswith('$INCLUDE') ):
          include_file_name = line.split('$INCLUDE')[1].lstrip().rstrip()
          if( not include_file_name.startswith('/') ):
            include_file_name = os.path.join(zone_file_dir, include_file_name)

          include_lines = []
          try:
            include_file = open(include_file_name, 'r')
            try:
              for line in include_file:
                include_lines.append(line)
            finally:
              include_file.close()
          except IOError:
            raise IncludeError('Unable to import include file: %s' % include_file_name)
          
          zone_lines.extend(include_lines)
          continue   
          
        zone_lines.append(line)
        
    finally:
      zone_file.close() 
        

    self.zone_file_string = unicode('\n'.join(zone_lines))

    self.zone_name = zone_name
    self.view = view

    zones_dict = self.core_instance.ListZones(zone_name=zone_name)
    if( zone_name in zones_dict ):
      zones_dict = zones_dict[zone_name]
      if( view in zones_dict ):
        zones_dict = zones_dict[view]
        self.origin = zones_dict[u'zone_origin']
      else:
        raise errors.InvalidInputError('View %s does not exist.' % view)
    else:
      raise errors.InvalidInputError('Zone %s does not exist.' % zone_name)

    self.all_views = self.core_instance.ListZones(zone_name=zone_name)[
        zone_name]


  def ReverseZoneToCIDRBlock(self):
    """Creates CIDR block from reverse zone name.

    Outputs:
      string of cidr block
    """
    if( self.origin.endswith('in-addr.arpa.') ):
      ip_parts = self.origin.split('.in-')[0].split('.')
      ip_parts.reverse()
      for ip_part in ip_parts:
        if( not ip_part.isdigit() ):
          raise Error('%s is not a reverse zone.' % self.zone_name)

      cidr_block = '.'.join(ip_parts)
      ip_octets = len(ip_parts)

      if( ip_octets > 3 or ip_octets < 1 ):
        raise Error('%s is not a reverse zone.' % self.zone_name)

      cidr_block = '%s/%s' % (cidr_block, ip_octets * 8)

    elif( self.origin.endswith('ip6.arpa.') ):
      ip_parts = self.origin.split('.ip6')[0].split('.')
      ip_parts.reverse()
      ip_quartets = len(ip_parts)

      for ip_part in ip_parts:
        try:
          int(ip_part, 16)
        except ValueError:
          raise Error('Invalid hexidecimal number in ipv6 origin: %s' %
                      self.origin)
      # fill out the rest of the ipv6 address
      ip_parts.extend(['0' for x in range(32-ip_quartets)])

      for x in range(1, 8):
        # Put colons every 4 quartets
        ip_parts.insert((x*4)+(x-1), ':')
      cidr_block = ''.join(ip_parts)

      cidr_block = '%s/%s' % (cidr_block, ip_quartets * 4)

    else:
      raise Error('%s is not a reverse zone.' % self.zone_name)

    return cidr_block
    
  def MakeRecordsFromZone(self):
    """Makes records in the database from dns.zone class.

    Outputs:
      int: Amount of records added to db.
    """
    return self.core_helper_instance.AddFormattedRecords(
        self.zone_name, self.zone_file_string, self.view)
