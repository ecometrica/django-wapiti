from piston.utils import rc

from ecoapi.views.base_view import EcoApiBaseView

class TopLevelInterfaceView(EcoApiBaseView):
    def get(self, request):
        return rc.NOT_IMPLEMENTED

class InterfaceView(EcoApiBaseView):
    def get(self, request, ver):
        return rc.NOT_IMPLEMENTED

