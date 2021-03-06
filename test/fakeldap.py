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

"""Fake ldap library with limited functionality"""

__copyright__ = 'Copyright (C) 2009, Purdue University'
__license__ = 'BSD'
__version__ = '#TRUNK#'


import roster_core


OPT_X_TLS = None
OPT_X_TLS_CACERTFILE = None

def set_option(option, value):
  pass

def VERSION3(self):
  pass

class LDAPError(roster_core.CoreError):
  pass

class AuthenticationMethod(object):

  def __init__(self, server=None):
    self.protocol_version = 0

  def Authenticate(self, user_name=None, binddn=None, password=None,
                   server=None):
    binddn = binddn % user_name
    if( binddn == 'uid=shuey,ou=People,dc=dc,dc=university,'
                  'dc=edu' and password == 'testpass' ):
      return True
    elif( binddn == 'uid=sharrell,ou=People,dc=dc,dc=university,'
                    'dc=edu' and password == 'test' ):
      return True
    elif( binddn == 'uid=jcollins,ou=People,dc=dc,dc=university,'
                    'dc=edu' and password == 'test' ):
      return True
    elif( binddn.startswith('uid=user') and password == 'tost' ):
      return True
    else:
      return False

  def unbind_s(self):
    pass

  def simple_bind_s(self, binddn, password):
    if( binddn == 'uid=jcollins,ou=People,dc=dc,dc=university,dc=edu' and
        password == 'test' ):
      pass
    else:
      raise LDAPError()

initialize = AuthenticationMethod
