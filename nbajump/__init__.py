#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) Giacomo Terreran (2021)
#
# This file is part of nbajump
#
# nbajump is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# nbajump is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with nbajump.  If not, see <http://www.gnu.org/licenses/>

"""nbajump
"""

from ._version import get_versions
__version__ = get_versions()['version']
__author__ = 'Giacomo Terreran <giacomo.terreran@northwestern.edu>'
__credits__ = ['Scott Coughlin <scottcoughlin2014@u.northwestern.edu>']
del get_versions
