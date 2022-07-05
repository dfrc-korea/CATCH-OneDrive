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

    OneDrive Internal APIs 를 사용하기 위해 필요한 인증정보(cookie, parameter, header) 수집하는 모듈

    도구이름    : Cloud Data Acquisition through Comprehensive and Hybrid Approaches(CATCH)\n
    프로젝트    : Cloud Data Acquisition through Comprehensive and Hybrid Approaches\n
    연구기관    : 고려대학교(Korea Univ.)\n

History
===========

    * 2022-05-18 : 초기 버전
    * 2022-06-01 : *로그인 Personal 만 가능하게 수정 -- 추후 변경 여부 파악
    * 2022-06-13 : 코드 안정화 -- add login wait time(sol>> cid, caller)
    * 2022-06-22 : 개인 중요 보관소 제거

"""

from module.CATCH_Cloud_Define import *

class Authentication:
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
        # 버그 존재 사용 금지

        try:
            with sync_playwright() as playwright:
                # TRUE = 화면 안보임, FALSE = 화면 보임
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context()

                # Open new page
                page = context.new_page()

                page.goto("https://onedrive.live.com/about/ko-kr/signin/")

                page.frame_locator("section[role=\"main\"] iframe").locator("[placeholder=\"전자 메일\\, 휴대폰 또는 Skype\"]").click()
                page.frame_locator("section[role=\"main\"] iframe").locator("[placeholder=\"전자 메일\\, 휴대폰 또는 Skype\"]").fill(self.__id)
                page.wait_for_timeout(1000)
                page.frame_locator("section[role=\"main\"] iframe").locator("[placeholder=\"전자 메일\\, 휴대폰 또는 Skype\"]").press(
                    "Enter")

                # Click text=사용자가 만든 계정
                page.wait_for_timeout(1000)
                try:
                    if page.frame_locator("section[role=\"main\"] iframe").locator("text=자세한 정보 필요").is_visible():
                        #p_or_b = input(Colors.YELLOW + "[>>] Which Account? Business: 1, Personal: 2  >>" + Colors.RESET)
                        p_or_b = 2
                        if p_or_b == 1:
                            with page.expect_navigation():
                                page.frame_locator("section[role=\"main\"] iframe").locator("text=IT 부서에서 만든 계정").click()
                                PRINT('Access - Business')
                        else:
                            with page.expect_navigation():
                                page.frame_locator("section[role=\"main\"] iframe").locator("text=사용자가 만든 계정").click()
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
                if page.locator("text=본인 여부 확인").is_visible():
                    factor2_texts = page.locator("div[role=\"button\"]").all_inner_texts()
                    cnt = 1
                    if len(factor2_texts) > 1:
                        for factor2_text in factor2_texts:
                            PRINTI(str(cnt) + '. ' + factor2_text.replace('\n', ''))
                            cnt += 1
                        factor2_cnt = input("몇 번째로 인증하시겠습니까? >> ")
                        page.locator("div[role=\"button\"]").locator(
                            "text =" + factor2_texts[int(factor2_cnt) - 1].replace('\t', '').replace('\n', '')).click()
                    else:
                        with page.expect_navigation():
                            page.locator("div[role=\"button\"]").click()

                    page.wait_for_timeout(500)
                    if page.locator("text=전화 번호 확인").is_visible():
                        # SMS
                        PRINTI(page.locator("xpath=//*[@id=\"idDiv_SAOTCS_ProofConfirmationDesc\"]").text_content())
                        factor2_sms = input("전화 번호 마지막 4자리를 넣어주세요 >>")
                        page.locator("xpath=//*[@id=\"idTxtBx_SAOTCS_ProofConfirmation\"]").fill(factor2_sms)
                        page.locator("xpath=//*[@id=\"idSubmit_SAOTCS_SendCode\"]").click()
                    else:
                        # E-mail
                        PRINTI(page.locator("xpath=//*[@id=\"idDiv_SAOTCC_Description\"]").text_content())

                    page.wait_for_timeout(500)
                    factor2 = input("코드를 넣어주세요 >>")
                    page.locator("[placeholder=\"코드\"]").click()
                    page.locator("[placeholder=\"코드\"]").fill(factor2)
                    page.locator("input:has-text(\"확인\")").click()

                elif page.locator("text=로그인 요청 승인").is_visible():
                    # App Login
                    PRINTI(page.locator("xpath=//*[@id=\"idDiv_SAOTCAS_Description\"]").text_content())
                    factor2 = input("승인이 완료되면 엔터를 눌러주세요.")

                # 영구 저장 '아니오' 클릭
                with page.expect_navigation():
                    page.locator("text=아니요").click()
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

                # context.close()
                # browser.close()

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

        if response.status_code is not 200:
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