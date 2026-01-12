# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


"""General utilities for the Rocket Workbench"""

__title__ = "General utilities for the Rocket Workbench"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

def _msg(message):
    """Write messages to the console including the line ending."""
    print(message + "\n")

def _wrn(message):
    """Write warnings to the console including the line ending."""
    print(message + "\n")

def _err(message):
    """Write errors  to the console including the line ending."""
    print(message + "\n")

def _trace(className, functionName, message = None):
    """Write errors  to the console including the line ending."""
    trace = True
    if trace:
        if message is None:
            print("%s:%s()\n" % (className, functionName))
        else:
            print("%s:%s(%s)\n" % (className, functionName, message))

def _toFloat(input, defaultValue = 0.0):
    if input == '':
        return defaultValue
    return float(input.rstrip(','))

def _toInt(input, defaultValue = 0):
    if input == '':
        return defaultValue
    return int(input.rstrip(','))

def _toBoolean(value):
    if str(value).strip().lower() == "true":
        return True
    return False
