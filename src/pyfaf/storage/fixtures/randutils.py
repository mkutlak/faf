# Copyright (C) 2013  ABRT Team
# Copyright (C) 2013  Red Hat, Inc.
#
# This file is part of faf.
#
# faf is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# faf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with faf.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division
import os
import random
import hashlib

from typing import Collection, Sequence, Union

def pickhalf(objects) -> Union[Sequence, Collection]:
    '''
    Randomly pick half of the objects
    '''
    return random.sample(objects, len(objects)//2)

def pickmost(objects) -> Union[Sequence, Collection]:
    '''
    Randomly pick 9/10 of the objects
    '''
    return random.sample(objects, len(objects)-len(objects)//10)

def toss() -> bool:
    '''
    Coin toss
    '''
    return bool(random.randrange(2))

def tosshigh() -> bool:
    '''
    High probability coin toss (9 of 10)
    '''
    return bool(random.randrange(10))

def tosslow() -> bool:
    '''
    Low probability coin toss (1 of 10)
    '''
    return not bool(random.randrange(10))

def randhash() -> str:
    '''
    Returns random sha1 hash
    '''
    return hashlib.sha1(os.urandom(30).encode("utf-8")).hexdigest()
