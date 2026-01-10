# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2022 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


"""Interface for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from Rocket.interfaces.Instanceable import Instanceable

class Clusterable(Instanceable):

    # @abstractmethod
    def getClusterConfiguration(self):
        raise NotImplementedError

    # @abstractmethod
    def setClusterConfiguration(self, cluster):
        raise NotImplementedError

    # @abstractmethod
    def getClusterSeparation(self):
        raise NotImplementedError
