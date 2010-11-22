from piston.utils import rc

from wapiti.views.base_view import wapitiBaseView

class TopLevelInterfaceView(wapitiBaseView):
    def get(self, request):
        return rc.NOT_IMPLEMENTED

class InterfaceView(wapitiBaseView):
    def get(self, request, ver):
        return rc.NOT_IMPLEMENTED

