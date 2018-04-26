# python-snpp: Provide SNPP functionality for Python.
# Copyright (C) 2002, 2007, 2010 by Monty Taylor
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from snpplib import *

class PagerException(Exception):
    """Base class for all exceptions raised by this module."""

class PagerInitialize(PagerException):
    """Initialization Failed

    Called when a Pager is unable to initialize.
    """
    
class Pager:

    server=None
    login=None
    
    def __init__(self, recips=[], message=None, host=SNPP_HOST, port=SNPP_PORT, debuglevel=0, server=None ):
        """Creates a Pager object.

        recips should be an array of Recipients
        message should be a Message

        The page will be sent to each of the Recipients, using an SNPP server determined one of two ways.
        a) Pass in an instantiated SNPP object as server
        b) failing that, if any or none of host, port or debuglevel are passed, an SNPP server will be created.

        To prevent the creation of an SNPP server (I don't know why, but hey, that's your call) pass in None for the
        host parameter
        """

        serverdebug=0
        self.recips=recips
        self.message=message
        if server:
            self.server=server
        elif host:
            self.server=SNPP(host=host, port=port, debuglevel=debuglevel)
        else:
            raise PagerInitialize(args=[recips,message,host,port,debuglevel,server])
        self.recip_cmds={ 'alert': self.server.alert,
                 'level': self.server.level,
                 'time':  self.hold_until,
                 'coverage': self.server.coverage }
        self.mess_cmds={  'callerid': self.server.callerid,
                 'subject': self.server.subject }

    def add_recipient(self, recip):

        if type(recip) == type([]):
            self.recips[len(self.recips):]=recip
        else:
            self.recips[len(self.recips):]=[recip]

    def del_recipient(self, recip):
        loop=0
        while loop < len(self.recips):
            if self.recips[loop] == recip:
                del self.recips[loop]
            else:
                loop=loop+1

    def set_login(self, login, password=None):
        self.login=login
        if password:
            self.password=password

    def _get_parm(self, recip, parm):
        if recip and hasattr(recip, parm) and getattr(recip,parm):
            return getattr(recip, parm)
        elif hasattr(self.message, parm) and getattr(self.message,parm):
            return getattr(self.message, parm)
        return None

    def _run_cmds(self, cmds, recip=None):
        for attr in cmds.keys():
                _attr=self._get_parm(recip=recip,parm=attr)
                if _attr:
                    cmds[attr](_attr)
                    
    def hold_until(self, time):

        if not time=='now':
            return self.server.holduntil(time=time)
            
        
    def send(self):

        # First step -- login
        if hasattr(self, 'login') and self.login:
            passwd=''
            if hasattr(self, 'password'):
                passwd=self.password
            self.server.login(login=self.login,password=passwd)

        # Now execute any recipient oriented commands, using the value held by
        # the recipient, or the value held global to the message
        for recip in self.recips:
            self._run_cmds(cmds=self.recip_cmds, recip=recip)   
            self.server.pager(id=recip.id, pin=recip.pin)

        # Now run message oriented commands
        self._run_cmds(cmds=self.mess_cmds,recip=None)

        if self.message.is_twoway():
            self.server.twoway()
            for response in self.message.get_responses():
                self.server.mcresponse(seed=response.get_seed(),text=response.get_text())

            self.server.data(self.message.get_message())
            (code, msg) = self.server.send()
            ( tag, pass_code, msg ) = string.split(msg,None,3)
            return _SentPage(code=code, tag=tag, pass_code=pass_code, msg=msg, server=self.server)

        self.server.data(self.message.get_message())
        (code, msg) = self.server.send()
        return Response(seed=code, text=msg)

    def quit(self):
        self.server.quit()

class _SentPage:
    """Returned to hold information about two way pages.
    Allows the user to query status. This class should not be created directly.
    """

    def __init__(self, code, tag, pass_code, msg, server):
        self.code=code
        self.tag=tag
        self.pass_code=pass_code
        self.msg=msg
        self.server=server

    def status(self):
        return self.server.mcstatus(tag=self.tag, code=self.code)
        
    
class MRBase:

    """ Base class for Message and Recipient.
    Defines four properties that can be present in the Recipient or in the Message:
      time,
      level,
      alert,
      coverage

    The methods are basically just Get and Set methods for each property.
    """
    
    time=None
    level=None
    alert=None
    coverage=None

    def set_hold(self, time):
        self.time=time

    def set_level(self, level):
        if level < 0 or level > 11:
            raise SNPPException
        self.level=level

    def set_alert(self):
        self.alert=1

    def set_coverage(self, coverage):
        self.coverage=coverage
        
    def get_hold(self):
        return self.time

    def get_level(self):
        return self.level

    def get_alert(self):
        return self.alert

    def get_coverage(self):
        return self.coverage
    
    def reset_hold(self):
        self.time=None

    def reset_level(self):
        self.level=None

    def reset_alert(self):
        self.alert=None

    def reset_coverage(self):
        self.coverage=None

class Message(MRBase):
    """Message class.

    Defines:
      message, (text of the message to be sent)
      callerid, (id to be sent for CALLerid function)
      subject, (subject of the message)
      responses (list of possible key/value response code pairs for a message)
      
    This class holds information about messages to be sent and properties that
    are only global to a message. Also holds global options for recipeint level options
    """

    message=None
    callerid=None
    subject=None
    responses=[]
    
    
    def __init__(self, message):
        self.message=message

    def set_message(self, message):
        self.message=message

    def set_callerid(self, id):
        self.callerid=id

    def set_subject(self, subject):
        self.subject=subject

    def get_message(self):
        return self.message

    def get_callerid(self):
        return self.callerid

    def get_subject(self):
        return self.subject

    def set_twoway(self):
        self.twoway = 1
        
    def is_twoway(self):
        return hasattr(self, 'twoway') and self.twoway == 1
    
    def add_response(self, response):
        self.twoway = 1
        if type(response) == type([]):
            self.responses[len(self.responses):]=response
        else:
            self.responses[len(self.responses):]=[response]

    def get_responses(self):
        return self.responses


class Recipient(MRBase):

    """ Class for the recipient of a page.

    Defines two properties:
      id,
      pin.

    Id is required. pin is optional.
    Methods are generic Get and Set methods for the properties, with one exception, send_now().
    
    Since the default behavior for a hold is to send now unless a value is set, a special value had to be
    created internally to distinguish the case where the Message has a hold time, but one Recipient wants
    to send now.
    """
    
    id=None
    pin=''
    
    def __init__(self, id, pin=''):
        self.id=id
        self.pin=pin

    def set_id(self, id):
        self.id=id

    def set_pin(self, pin):
        self.pin=pin
        
    def get_id(self):
        return self.id

    def get_pin(self):
        return self.pin

    def send_now(self):
        self.time='now'

class Response:
    """Class representing a possible key/value response for a message

    Defines:
      seed, (two-byte code)
      text, (text to pair with the seed)
    """

    def __init__(self, seed, text):
        self.seed=seed
        self.text=text

    def set_seed(self,seed):
        self.seed=seed

    def set_text(self,text):
        self.text=text
        
    def get_seed(self):
        return self.seed

    def get_text(self):
        return self.text



if __name__=='__main__':

    host='localhost'
    port=444
    debuglevel=1

    #server=SNPP(host=host, port=port, debuglevel=debuglevel)

    bob=Recipient(id='5551212')
    larry=Recipient(id='4773822',pin='9999')
    larry.send_now()

    mess=Message(message='The server is down')
    mess.set_hold('001231101103')
    #mess.set_subject(subject='HELP')

    page=Pager( recips=[bob], message=mess, host=host, port=port, debuglevel=debuglevel)
    page.add_recipient(bob)
   
    page1=page.send()
    print type(page1)

    mess.set_message(message="Wow! It's really down this time")

    mess.set_twoway()
    spam=Recipient(id='1234567')
    eggs=Recipient(id='0877639184')
    page.add_recipient([spam, eggs])
    page.del_recipient(bob)
    page2=page.send()
    print type(page2)
    page.quit()

