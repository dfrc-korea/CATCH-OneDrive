from playwright.sync_api import Playwright as playwright
from playwright.sync_api import sync_playwright, expect
from termcolor import colored
from pyfiglet import Figlet
import requests
import json
import tabulate
import datetime, re
import termcolor
import time, os, sys
import urllib3
import time
import pytz
import dateutil.parser
import onedrivesdk_fork as onedrivesdk
from onedrivesdk_fork.helpers import GetAuthCodeServer
import time
from pathlib import Path
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#--------------------service----------------------
SERVICES = ['', 'Google Drive', 'OneDrive', 'DropBox', 'BOX', 'MEGA']

CA_ERROR        = 0
CA_OK           = 1

# -*- coding: utf-8 -*-

BRIGHT_BLACK = '\033[90m'
BRIGHT_RED = '\033[91m'
BRIGHT_GREEN = '\033[92m'
BRIGHT_YELLOW = '\033[93m'
BRIGHT_BLUE = '\033[94m'
BRIGHT_MAGENTA = '\033[95m'
BRIGHT_CYAN = '\033[96m'
BRIGHT_WHITE = '\033[97m'
BRIGHT_END = '\033[0m'

class Colors:
	BLACK = '\033[30m'
	RED = '\033[31m'
	GREEN = '\033[32m'
	YELLOW = '\033[33m'
	BLUE = '\033[34m'
	MAGENTA = '\033[35m'
	CYAN = '\033[36m'
	WHITE = '\033[37m'
	UNDERLINE = '\033[4m'
	RESET = '\033[0m'

class Background:
	BLACK = '\033[40m'
	RED = '\033[41m'
	GREEN = '\033[42m'
	YELLOW = '\033[43m'
	BLUE = '\033[44m'
	MAGENTA = '\033[45m'
	CYAN = '\033[46m'
	WHITE = '\033[47m'

class CA_log(object):
	fp = None
	loglevel = 0
	CA_D = ["debug", "blue", 3]
	CA_I = ["info", "green", 2]
	CA_E = ["error", "red", 0]

	@staticmethod
	def set_loglevel(__loglevel):
		CA_log.loglevel = __loglevel

	@staticmethod
	def log_write(level, text, enter=1, attr=None):
		__level = []
		__loglevel = CA_log.loglevel
		if level == "CA_D":
			__level = CA_log.CA_D
		elif level == "CA_I":
			__level = CA_log.CA_I
		elif level == "CA_E":
			__level = CA_log.CA_E

		if CA_log.fp is None:
			if __level[2] <= __loglevel:
				if enter == 0:
					return print(termcolor.colored("[" + __level[0] + "] " + text, color=__level[1], attrs=attr),
								 end='', flush=True)
				else:
					return print(termcolor.colored("[" + __level[0] + "] " + text, color=__level[1], attrs=attr))
		else:
			if __level[2] <= __loglevel:
				CA_log.fp.write("[" + __level[0] + "] " + text + "\n")

	@staticmethod
	def set_log_fp(output_path, method, modulename="DA"):
		if method is True:
			d = datetime.datetime.today()
			__output_path = output_path + os.sep + modulename + "_" + d.strftime('%y%m%d_%H%M%S_') + str(
				os.getpid()) + ".log"
			CA_log.fp = open(__output_path, 'w', encoding='utf16')
		else:
			CA_log.fp = None

	@staticmethod
	def close_log_fp():
		if CA_log.fp is None:
			pass
		else:
			CA_log.fp.close()


def PRINT(message):
    if type(message) == type(str):
        CA_log.log_write("CA_D", message)
    else:
        CA_log.log_write("CA_D", str(message))


def PRINTI(message):
    if type(message) == type(str):
        CA_log.log_write("CA_I", message)
    else:
        CA_log.log_write("CA_I", str(message))


def PRINTE(message):
    if type(message) == type(str):
        CA_log.log_write("CA_E", message)
    else:
        CA_log.log_write("CA_E", str(message))

class CInput:

    def __init__(self):
        self.__keyword_name = None
        self.__keyword_text = None
        self.__m_period = list()

    def set_m_period(self):
        self.__set_m_period()
        return self.__m_period

    def set_gdrive_inputs(self):
        # 1. keyword
        self.__set_keyword_name()
        self.__set_keyword_text()
        # 2. modified
        self.__set_m_period()

    def __set_keyword_name(self):
        print("\n"
              "Set keyword to search in name.\n"
              "If you don't want to set keyword, hit enter.\n"
              "Example input: police")
        self.__keyword_name = input("Put keyword: ")

    def __set_keyword_text(self):
        print("\n"
              "Set keyword to search in full text.\n"
              "If you don't want to set keyword, hit enter.\n"
              "Example input: lab")
        self.__keyword_text = input("Put keyword: ")

    def __set_m_period(self):
        print("\n"
              "Set period to search modified time.\n"
              "If you don't want to set period, hit enter.\n"
              "Example input: 2021-06-04")
        check = re.compile(r"\d\d\d\d-\d\d-\d\d")
        while True:
            start_time = input("Put start time: ")
            if check.fullmatch(start_time) != None:
                break
            elif start_time == "":
                start_time = "1970-01-01"
                break
            else:
                print(" [!] Invalid format.")
        while True:
            end_time = input("Put end time: ")
            if check.fullmatch(end_time) != None:
                break
            elif end_time == "":
                end_time = datetime.datetime.now().strftime("%Y-%m-%d")
                break
            else:
                print(" [!] Invalid format.")

        self.__m_period.append(start_time)
        self.__m_period.append(end_time)

    def get_keyword_name(self):
        return self.__keyword_name

    def get_keyword_text(self):
        return self.__keyword_text

    def get_m_period(self):
        return self.__m_period

    def show_input(self):
        print("\n"
              "======SHOW_INPUT======")
        print("Keyword-name : ", self.__keyword_name)
        print("Keyword-text : ", self.__keyword_text)
        print("Period-modified : ", self.__m_period)
