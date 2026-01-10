# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2021 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
