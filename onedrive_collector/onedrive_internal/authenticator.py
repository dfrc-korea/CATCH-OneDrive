"""
============================================
    "authenticator" Module
============================================
.. moduleauthor:: Jihyeok Yang <piki@korea.ac.kr>

.. note::
    'TITLE'             : OneDrive - Authenticator in CATCH\n
    'AUTHOR'            : Jihyeok Yang\n
    'TEAM'              : DFRC\n
    'VERSION'           : 0.0.4\n
    'RELEASE-DATE'      : 2022-05-18\n

--------------------------------------------

Description
===========

    A module that collects credentials (cookie, parameter, header) required to use OneDrive Internal APIs

    Tool        : Cloud Data Acquisition through Comprehensive and Hybrid Approaches(CATCH)\n
    Project     : Cloud Data Acquisition through Comprehensive and Hybrid Approaches\n
    Research    : Korea Univ. Digital Forensic Research Center(DFRC)\n

History
===========

    * 2022-05-18 : 1st Version
    * 2022-06-01 : Login
    * 2022-06-13 : Add login wait time(sol>> cid, caller)

"""

from module.CATCH_Cloud_Define import *

class Authentication:
    """Authentication Class

        .. note::  To collect authentication information, attempt to login using browser automation
    """
    def __init__(self, credential):
        self.__id = credential[0]
        self.__password = credential[1]
        self.__all_cookies = None
        self.__cookie_wlssc = None
        self.__cookie_msa_auth = None
        self.__cid = None
        self.__caller = None
        self.__after_login_url = None
        self.__header_canary = None

    def run(self):
        """Authentication run method

                .. note::  Parse authentication information \n
                    login() : Login using Browser Automation \n
                    set_auth_value() : Collect essential values(Cookie: WLSSC, msa_auth) \n
                    set_header_value() : Collect essential values using Request(Header value: Canary) \n

                :return:
                    success  --  CA_OK
                    fail     --  CA_ERROR
        """
        if self.__login() == CA_ERROR:
            PRINT('Login Error')
            return CA_ERROR

        if self.__set_auth_value() == CA_ERROR:
            PRINT('Set Authentication Value Error')
            return CA_ERROR

        if self.__set_header_value() == CA_ERROR:
            PRINT('Set Header Value Error')

        return CA_OK

    def __login(self):
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context()

                # Open new page
                page = context.new_page()

                page.goto("https://onedrive.live.com/about/en-us/signin/")

                page.frame_locator("section[role=\"main\"] iframe").locator(
                    "//*[@id=\"placeholder\"]/div[2]/div/input").click()
                page.frame_locator("section[role=\"main\"] iframe").locator(
                    "//*[@id=\"placeholder\"]/div[2]/div/input").fill(self.__id)
                page.wait_for_timeout(1000)
                page.frame_locator("section[role=\"main\"] iframe").locator(
                    "//*[@id=\"placeholder\"]/div[2]/div/input").press(
                    "Enter")

                page.wait_for_timeout(1000)
                try:
                    if page.frame_locator("section[role=\"main\"] iframe").locator("text=We need a little more help").is_visible():
                        # CATCH select personal default (Changeable)
                        #p_or_b = input(Colors.YELLOW + "[>>] Which Account? Business: 1, Personal: 2  >>" + Colors.RESET)
                        p_or_b = 2
                        if p_or_b == 1:
                            with page.expect_navigation():
                                page.frame_locator("section[role=\"main\"] iframe").locator("text=Created by your IT department").click()
                                PRINT('Access - Business')
                        else:
                            with page.expect_navigation():
                                page.frame_locator("section[role=\"main\"] iframe").locator("text=Created by you").nth(
                                    1).click()
                                PRINT('Access - Personal')
                    else:
                        PRINT('Access')
                except:
                    pass

                page.locator("input[name=\"passwd\"]").fill(self.__password)

                with page.expect_navigation():
                    page.locator("input[name=\"passwd\"]").press("Enter")

                page.wait_for_timeout(500)
                # SMS, E-mail
                if page.locator("text=Verify your identity").is_visible():
                    factor2_texts = page.locator("div[role=\"button\"]").all_inner_texts()
                    cnt = 1
                    if len(factor2_texts) > 1:
                        for factor2_text in factor2_texts:
                            PRINTI(str(cnt) + '. ' + factor2_text.replace('\n', ''))
                            cnt += 1
                        factor2_cnt = input("What number would you like to use to authenticate? >> ")
                        page.locator("div[role=\"button\"]").locator(
                            "text =" + factor2_texts[int(factor2_cnt) - 1].replace('\t', '').replace('\n', '')).click()
                    else:
                        with page.expect_navigation():
                            page.locator("div[role=\"button\"]").click()

                    page.wait_for_timeout(500)
                    if page.locator("text=Verify your phone number").is_visible():
                        # SMS
                        PRINTI(page.locator("xpath=//*[@id=\"idDiv_SAOTCS_ProofConfirmationDesc\"]").text_content())
                        factor2_sms = input("Last 4 digits of phone number >>")
                        page.locator("xpath=//*[@id=\"idTxtBx_SAOTCS_ProofConfirmation\"]").fill(factor2_sms)
                        page.locator("xpath=//*[@id=\"idSubmit_SAOTCS_SendCode\"]").click()
                    else:
                        # E-mail
                        PRINTI(page.locator("xpath=//*[@id=\"idDiv_SAOTCC_Description\"]").text_content())

                    page.wait_for_timeout(500)
                    factor2 = input("Enter code >>")
                    page.locator("[placeholder=\"Code\"]").click()
                    page.locator("[placeholder=\"Code\"]").fill(factor2)
                    page.locator("input:has-text(\"Verify\")").click()

                elif page.locator("text=Approve sign in request").is_visible():
                    # App Login
                    PRINTI(page.locator("xpath=//*[@id=\"idDiv_SAOTCAS_Description\"]").text_content())
                    factor2 = input("Please press Enter when approval is completed.")

                # Click on 'No' to save permanently
                with page.expect_navigation():
                    page.locator("text=No").click()
                page.wait_for_timeout(1000)

                # ---------------------
                page.wait_for_timeout(1000)
                while True:
                    if "gologin" in page.url:
                        page.goto(page.url)
                        page.wait_for_timeout(1000)
                    else:
                        break

                self.__caller = page.url[page.url.find("cid=") + 4:]
                self.__all_cookies = page.context.cookies()

                return CA_OK

        except Exception as e:
            PRINTE(e)
            return CA_ERROR

    def __set_auth_value(self):
        if len(self.__all_cookies) == 0:
            return CA_ERROR

        try:
            with requests.Session() as s:
                for cookie in self.__all_cookies:
                    s.cookies.set(cookie['name'], cookie['value'])
                    if 'msa_auth' in cookie['name']:
                        self.__cookie_msa_auth = cookie['value']

            self.__cookie_wlssc = s.cookies.get("WLSSC")
            self.__cid = self.__caller
        except:
            return CA_ERROR

        return CA_OK

    def __set_header_value(self):
        """
            .. note:: Need to parse javascript(response)

        """
        cookies = {
            'WLSSC': self.__cookie_wlssc,
        }

        headers = {
            'Host': 'onedrive.live.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Referer': 'https://login.live.com/',
            'Accept-Encoding': 'deflate',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        params = (
            ('lc', '2066'),
            ('sw', 'bypassConfig'),
        )

        response = requests.get('https://onedrive.live.com/', headers=headers, params=params, cookies=cookies,
                                verify=False)

        if response.status_code == 404:
            PRINTE("Request URL is Changed")
            return CA_ERROR

        self.__header_canary = response.content.split(b"FilesConfig=")[1].split(b',')[0].decode('unicode_escape')[11:-1]

        return CA_OK

    def get_cookie_wlssc(self):
        return self.__cookie_wlssc

    def get_cookie_msa_auth(self):
        return self.__cookie_msa_auth

    def get_header_canary(self):
        return self.__header_canary

    def get_parameter_cid(self):
        return self.__cid

    def get_parameter_caller(self):
        return self.__caller