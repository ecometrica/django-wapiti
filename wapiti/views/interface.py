# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
from piston.utils import rc

from wapiti.views.base_view import WapitiBaseView

class TopLevelInterfaceView(WapitiBaseView):
    def get(self, request):
        return rc.NOT_IMPLEMENTED

class InterfaceView(WapitiBaseView):
    def get(self, request, ver):
        return rc.NOT_IMPLEMENTED

