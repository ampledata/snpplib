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

# bootstrap setuptools if necessary
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

classifiers="""\
Development Status :: 6 - Mature
License :: OSI Approved :: GNU General Public License (GPL)
Operating System :: POSIX :: Linux
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
"""

setup (name = "python-snpp",
       version = "1.1.2",
       description = "Libraries implementing RFC 1861 - Simple Network Paging Protocol",
       author = "Monty Taylor",
       author_email = "mordred@inaugust.com",
       url = "http://launchpad.net/python-snpp",
       license="GPL",
       classifiers=filter(None, classifiers.splitlines()),
       py_modules = ['snpplib','Pager'],

      )
