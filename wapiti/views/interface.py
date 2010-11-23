# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
from piston.utils import rc

from wapiti.views.base_view import wapitiBaseView

class TopLevelInterfaceView(wapitiBaseView):
    def get(self, request):
        return rc.NOT_IMPLEMENTED

class InterfaceView(wapitiBaseView):
    def get(self, request, ver):
        return rc.NOT_IMPLEMENTED

