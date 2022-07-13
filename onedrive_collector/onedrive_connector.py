from onedrive_collector.onedrive_internal.internal_core import *
from onedrive_collector.onedrive_open.open_core import *
import module.Cloud_Display as cd

class OneDrive_connector:
    def __init__(self):
        self.__mode = None
        self.__core = None

    def excute(self, credential):
        if self.__set_mode() == CA_ERROR:
            PRINTE("Set Acquisition Mode ERROR")
            return CA_ERROR

        if self.__core.run(credential) == CA_ERROR:
            PRINTE("Run Acquisition Module ERROR")
            return CA_ERROR
        return CA_OK

    def __set_mode(self):
        PRINTI("CATCH supports two acquisition mode: Open and Internal.")
        while True:
            try:
                self.__mode = int(input("Which mode would you like to use? (1:Open API, 2:Internal API) "))
                if self.__mode < 3 and self.__mode > 0:
                    break
            except:
                PRINTE("Please Input correct number.")

        if self.__mode == 1:
            self.__core = OneDrive_Open()
        elif self.__mode == 2:
            self.__core = OneDrive_Internal()

        return CA_OK