"""
============================================
    "PV_authenticator_and_explorer" Module
============================================
.. moduleauthor:: Jihyeok Yang <piki@korea.ac.kr>

.. note::
    'TITLE'             : OneDrive - Personal Vault in CATCH\n
    'AUTHOR'            : Jihyeok Yang\n
    'TEAM'              : DFRC\n
    'VERSION'           : 0.0.4\n
    'RELEASE-DATE'      : 2022-06-23\n

--------------------------------------------

Description
===========

    OneDrive Personal Vault 까지 포함한 데이터 수집을 위한 모듈

    도구이름    : Cloud Data Acquisition through Comprehensive and Hybrid Approaches(CATCH)\n
    프로젝트    : Cloud Data Acquisition through Comprehensive and Hybrid Approaches\n
    연구기관    : 고려대학교(Korea Univ.)\n

History
===========

    * 2022-06-23 : 초기 버전
    * 2022-06-23 : 개인 중요 보관소 추가 --> playwright 버그 존재 사용 잠정 정지

"""

from module.CATCH_Cloud_Define import *
from tqdm import tqdm

class Personal_Vault:
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
        self.__normal_file_list = []
        self.__number_of_normal_file = None
        self.__recycle_file_list = []
        self.__number_of_recycle_file = None
        self.__shared_file_list = []
        self.__number_of_shared_file = None
        self.__version_history = []
        self.__total_file_list = []
        self.__total_file_count = None
        self.__thumbnail_count = 0
        self.__total_version_count = 0
        self.__file_list = []
        self.__folder_list = []
        self.__flag = 1

    def run(self):
        if self.__login() == CA_ERROR:
            PRINT('Login Error')
            return CA_ERROR

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
                # 개인 중요 보관소 open

                PRINT("개인 중요 보관소는 인증코드가 필요합니다. 다음의 내용들을 입력해주세요.")
                time.sleep(1)
                with page.expect_navigation():
                    with page.expect_popup() as popup_info:
                        page.locator("text=개인 중요 보관소").click()
                        page.wait_for_timeout(1000)
                    page1 = popup_info.value

                if page1.locator("text=본인 여부 확인").is_visible():
                    factor2_texts = page1.locator("div[role=\"button\"]").all_inner_texts()
                    cnt = 1
                    if len(factor2_texts) > 1:
                        for factor2_text in factor2_texts:
                            PRINTI(str(cnt) + '. ' + factor2_text.replace('\n', ''))
                            cnt += 1
                        factor2_cnt = input("몇 번째로 인증하시겠습니까? >> ")
                        page1.locator("div[role=\"button\"]").locator(
                            "text =" + factor2_texts[int(factor2_cnt) - 1].replace('\t', '').replace('\n','')).click()
                    else:
                        with page1.expect_navigation():
                            page1.locator("div[role=\"button\"]").click()
                    page1.wait_for_timeout(500)

                    if page1.locator("text=전화 번호 확인").is_visible():
                        # SMS
                        PRINTI(page1.locator("xpath=//*[@id=\"idDiv_SAOTCS_ProofConfirmationDesc\"]").text_content())
                        factor2_sms = input("전화 번호 마지막 4자리를 넣어주세요 >>")
                        page1.locator("xpath=//*[@id=\"idTxtBx_SAOTCS_ProofConfirmation\"]").fill(factor2_sms)
                        page1.locator("xpath=//*[@id=\"idSubmit_SAOTCS_SendCode\"]").click()
                    else:
                        # E-mail
                        PRINTI(page1.locator("xpath=//*[@id=\"idDiv_SAOTCC_Description\"]").text_content())

                    page1.wait_for_timeout(500)
                    factor2 = input("코드를 넣어주세요 >>")
                    page1.locator("[placeholder=\"코드\"]").click()
                    page1.locator("[placeholder=\"코드\"]").fill(factor2)
                    page1.locator("input:has-text(\"확인\")").click()

                elif page1.locator("text=로그인 요청 승인").is_visible():
                    # App Login
                    PRINTI(page1.locator("xpath=//*[@id=\"idDiv_SAOTCAS_Description\"]").text_content())
                    factor2 = input("승인이 완료되면 엔터를 눌러주세요.")

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

                if self.__set_auth_value() == CA_ERROR:
                    PRINT('Set Authentication Value Error')
                    return CA_ERROR

                if self.__set_header_value() == CA_ERROR:
                    PRINT('Set Header Value Error')

                if self.__set_normal_file_list() == CA_ERROR:
                    PRINT('Set Normal File List Error')
                    return CA_ERROR

                if self.__set_recycle_file_list() == CA_ERROR:
                    PRINT('Set RecycleBin File List Error')
                    return CA_ERROR

                if self.__set_shared_file_list() == CA_ERROR:
                    PRINT('Set Shared File List Error')
                    return CA_ERROR

                if self.__combine_file_list() == CA_ERROR:
                    PRINT('Combine File List Error')
                    return CA_ERROR

                if self.__devide_file_list() == CA_ERROR:
                    PRINT('Divie File List Error')
                    return CA_ERROR

                if self.__download_thumbnails() == CA_ERROR:
                    PRINT('Collecting Thumbnails Error')
                    return CA_ERROR

                if self.__set_version_history() == CA_ERROR:
                    return CA_ERROR

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
            # ('mkt', ['ko-KR', 'ko-KR']),
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

    def get_flag(self):
        return self.__flag

    def __set_normal_file_list(self):
        try:
            file_list = self.__request_file_list()
            self.__normal_file_list = self.__remake_file_list(file_list, 'root')
            self.__number_of_normal_file = len(self.__normal_file_list)
            self.__flag = 0
        except Exception as e:
            PRINTE(e)
            return CA_ERROR

        return CA_OK

    def __set_recycle_file_list(self):
        try:
            file_list = self.__request_file_list(qt='recyclebin')
            self.__recycle_file_list = self.__remake_file_list(file_list, 'root', self.__recycle_file_list, qt='recyclebin')
            self.__flag = 0
            self.__number_of_recycle_file = len(self.__recycle_file_list)
        except:
            return CA_ERROR

        return CA_OK

    def __set_shared_file_list(self):
        try:
            file_list = self.__request_file_list(qt='sharedby')
            self.__shared_file_list = self.__remake_file_list(file_list, 'root', self.__shared_file_list, qt='sharedby')
            self.__flag = 0
            self.__number_of_shared_file = len(self.__shared_file_list)
        except:
            return CA_ERROR

        return CA_OK

    def __download_thumbnails(self):
        PRINT('Collecting Thumbnails Start')
        try:
            for child in tqdm(self.__total_file_list):
                if "thumbnailSet" in child:
                    self.__thumbnail_count += 1
                    self.__get_thumbnails(child['thumbnailSet'], child['name'])
        except:
            return CA_ERROR

        time.sleep(5)

        PRINT('Total file : ' + str(self.__total_file_count) + ' & Thumbnail Exist file : ' + str(self.__thumbnail_count))
        PRINT('Collecting Thumbnails Done')
        return CA_OK

    def __request_file_list(self, id='root', qt=''):
        cookies = {
            'WLSSC': self.__cookie_wlssc,
        }

        headers = {
            'Host': 'skyapi.onedrive.live.com',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'canary': self.__header_canary,
            'Accept': 'application/json',
            'AppId': '1141147648',
            'Accept-Encoding': 'deflate, br',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        if qt == '':
            params = (
                ('caller', self.__caller),
                ('d', '1'),
                ('id', id),
                ('cid', self.__cid),
                ('ps', 2000)
            )
        else:
            params = (
                ('caller', self.__caller),
                ('d', '1'),
                ('id', id),
                ('cid', self.__cid),
                ('qt', qt),
                ('ps', 2000)
            )

        response = requests.get('https://skyapi.onedrive.live.com/API/2/GetItems', headers=headers, params=params,
                                cookies=cookies, verify=False)

        return json.loads(response.text)

    def __remake_file_list(self, file_list, id='root', final_file_list=[], qt=''):
        folder_list = []
        # json 파일 떨구기
        if qt == 'recyclebin':
            name_id = 'recyclebin'
        elif qt == 'sharedby':
            name_id = 'sharedby'
        elif qt == '':
            name_id = id

        if not (os.path.isdir('./Json')):
            os.makedirs('./Json')

        with open('./Json/file_list_' + name_id + '.json', 'w', encoding='utf-8') as make_file:
            json.dump(file_list, make_file, ensure_ascii=False, indent='\t')
        PRINT('Extract json file done. >> file_list_' + name_id)

        root_folder = file_list['items'][0]['folder']
        child_count = root_folder['childCount']
        children = root_folder['children']
        if child_count == 0:
            return final_file_list

        if file_list['items'][0]['id'] == 'root':
            for child in children:
                if child['itemType'] == 32:
                    if child['name'] == '개인 중요 보관소' and self.__flag == 0:
                        pass
                    else:
                        final_file_list.append(child)
                        folder_list.append(child['eTag'][:child['eTag'].find('.')])
                else:
                    final_file_list.append(child)
        else:
            for child in children:
                if child['itemType'] == 32:
                    final_file_list.append(child)
                    folder_list.append(child['eTag'][:child['eTag'].find('.')])
                else:
                    final_file_list.append(child)

        for folder_id in folder_list:
            if qt == 'recyclebin':
                break
            file_list = self.__request_file_list(folder_id)
            final_file_list = self.__remake_file_list(file_list, folder_id, final_file_list)

        return final_file_list

    def __get_thumbnails(self, url_set, filename):
        if not (os.path.isdir('./thumbnails')):
            os.makedirs('./thumbnails')

        request_url = url_set['baseUrl'] + url_set['thumbnails'][1]['url']
        response = requests.get(request_url)

        with open('./thumbnails/' + filename + '.jpg', 'wb') as a:
            a.write(response.content)

    def __combine_file_list(self):
        self.__total_file_count = self.__number_of_normal_file + self.__number_of_recycle_file
        self.__total_file_list = self.__normal_file_list + self.__recycle_file_list

        if self.__total_file_count == 0:
            return CA_ERROR

        return CA_OK

    def __set_version_history(self):
        PRINT('Set Version History Start')

        try:
            for child in tqdm(self.__total_file_list):
                if child['itemType'] == 32:
                    continue
                else:
                    self.__get_file_version(child['id'])
                    self.__total_version_count += 1
        except:
            return CA_ERROR

        PRINT('Total file : ' + str(self.__total_file_count) + ' & Version History Exist file : ' + str(
            self.__total_version_count))
        PRINT('Set Version History Done')
        return CA_OK

    def __get_file_version(self, file_num):
        headers = {
            'Host': 'api.onedrive.com',
            'Connection': 'keep-alive',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Whale";v="3"',
            'Accept': 'application/json',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.57 Whale/3.14.133.23 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'Origin': 'https://onedrive.live.com',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://onedrive.live.com/',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        request_url = 'https://api.onedrive.com/v1.0/drive/items/' + file_num + '/versions?access_token=' + self.__cookie_msa_auth

        response = requests.get(request_url, headers=headers, verify=False)

        self.__version_history.append(json.loads(response.text))

    def get_total_file_list(self):
        return self.__total_file_list, self.__file_list, self.__folder_list

    def __devide_file_list(self):
        for file in self.__total_file_list:
            if 'folder' in file:
                self.__folder_list.append(file)
            else:
                self.__file_list.append(file)

        return CA_OK