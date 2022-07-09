"""
============================================
    "Cloud_Core" Module
============================================
.. moduleauthor:: Jihyeok Yang <piki@korea.ac.kr>
.. note::
    'TITLE'             : Cloud_Core python file in CATCH\n
    'AUTHOR'            : Jihyeok Yang\n
    'TEAM'              : DFRC\n
    'VERSION'           : 0.0.3\n
    'RELEASE-DATE'      : 2022-05-18\n

--------------------------------------------

Description
===========

    Module for collecting data stored on cloud storage

    Tool        : Cloud Data Acquisition through Comprehensive and Hybrid Approaches(CATCH)\n
    Project     : Cloud Data Acquisition through Comprehensive and Hybrid Approaches\n
    Research    : Korea Univ. Digital Forensic Research Center(DFRC)\n

Member
===========

    JH. Yang, JE. Kim, JW. Bang, SJ. Lee, JH. Park

History
===========

    * 2022-05-18 Yang(DFRC): 1st Version
    * 2022-05-20 Yang(DFRC): Add OneDrive_connector

Method
===========
"""
from onedrive_collector.onedrive_connector import *
import module.Cloud_Display as cd

class CA_Core():
    """ CA_Core Class
                "Core" Module's Main Class

            >>> "Example Code"
                CA_Core()
        """
    def __init__(self, loglevel=3):
        self.__loglevel = loglevel
        self.__service = None
        self.__connector = None
        self.__credential = None

    def run(self):
        """CA_Core run method

                .. note::  Start Core \n
                    set_default() : set Cloud storage and User credential \n
                    load_module() : Loads the selected cloud storage module. \n
                    run_module() : Run the selected cloud storage module. \n

                :return:
                    success  --  True
                    fail     --  False
        """
        cd.start_tool()

        if self.__set_default() == CA_ERROR:
            PRINTE("CATCH Cloud Setting Error")
            return False

        if self.__load_module() == CA_ERROR:
            PRINTE("Load Module Error")
            return False

        if self.__run_module() == CA_ERROR:
            PRINTE("Service Start Error")
            return False

        return True


    def __set_default(self):
        CA_log.set_loglevel(self.__loglevel)
        while True:
            try:
                self.__service = int(cd.select_cloud())
                break
            except:
                PRINTE("Please Input Correct Number(1~5)")
        if self.__service != 2:
            PRINTI("Under Development....")
            return CA_ERROR
        id, pw = cd.login_data()
        self.__credential = [id, pw]
        return CA_OK

    def __load_module(self):
        if self.__service not in [1, 2, 3, 4, 5]:
            return CA_ERROR

        PRINTI("Connecting.... " + SERVICES[self.__service])

        if self.__service == 1:
            self.__connector = OneDrive_connector()
        elif self.__service == 2:
            self.__connector = OneDrive_connector()
        elif self.__service == 3:
            self.__connector = OneDrive_connector()
        elif self.__service == 4:
            self.__connector = OneDrive_connector()
        elif self.__service == 5:
            self.__connector = OneDrive_connector()

        return CA_OK

    def __run_module(self):
        self.__connector.excute(self.__credential)

if __name__ == "__main__":
    a = CA_Core(3)
    a.run()