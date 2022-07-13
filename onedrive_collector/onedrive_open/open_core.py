import module.Cloud_Display as cd
from onedrive_collector.onedrive_open.open_API import *

class OneDrive_Open:
    def __init__(self):
        self.__redirect_uri = "http://localhost:8080/"
        self.__client_secret = "9-PA2Gjoq8It~4IhttDm0m_g.2.wLno0.4"
        self.__client_id = '2755a175-8423-49df-be40-c325a51a3d0d'
        pass

    def run(self, credential):
        my_onedrive = OneDrive(self.__redirect_uri, self.__client_secret, self.__client_id)
        result = my_onedrive.run()

        # for cnt, info in enumerate(result, start=1):
        #     export = Export(argv.export, "OneDrive_search_" + str(cnt))
        #     export.input_dict(info)
        # print(" [*] Export csv")