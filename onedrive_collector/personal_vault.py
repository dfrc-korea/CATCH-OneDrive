"""
============================================
    "Personal_Vault" Module
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

    Module for collecting data stored OneDrive with Personal Vault

    Tool        : Cloud Data Acquisition through Comprehensive and Hybrid Approaches(CATCH)\n
    Project     : Cloud Data Acquisition through Comprehensive and Hybrid Approaches\n
    Research    : Korea Univ. Digital Forensic Research Center(DFRC)\n

History
===========

    * 2022-06-23 : 1st Version
    * 2022-06-23 : Add Personal Vault --> playwright bug exists, You have to open a window

"""

from module.CATCH_Cloud_Define import *
import module.Cloud_Display as cd
from tqdm import tqdm

class Personal_Vault:
    """Personal_Vault Class

        .. note::  For Personal Vault, Browser Automation must be open in all processes.
                   This class do Authentication, Exploration, Filtering, Collection
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
        self.__normal_file_list = []
        self.__number_of_normal_file = None
        self.__recycle_file_list = []
        self.__number_of_recycle_file = None
        self.__shared_file_list = []
        self.__number_of_shared_file = None
        self.__recent_file_list = []
        self.__number_of_recent_file = None
        self.__version_history = []
        self.__total_file_list = []
        self.__total_file_count = None
        self.__thumbnail_count = 0
        self.__total_version_count = 0
        self.__file_list = []
        self.__folder_list = []
        self.__flag = 1
        self.__show_file_list = None
        self.__vault_name = None

    def run(self):
        if self.__login() == CA_ERROR:
            PRINT('Login Error')
            return CA_ERROR

        return CA_OK

    def __login(self):
        """Personal_Vault login method

                .. note::  Main method in Personal_Vault Class. \n
                           Log in using user credential and Browser Automation\n

                    set_auth_value() : Collect essential values(Cookie: WLSSC, msa_auth) \n
                    set_header_value() : Collect essential values using Request(Header value: Canary) \n
                    set_normal_file_list() : Request [My Files] Data and Parse JSON \n
                    set_recycle_file_list() : Request [Recycle Bin] Data and Parse JSON \n
                    set_shared_file_list() : Request [Shared] Data and Parse JSON \n
                    set_recent_file_list() : Request [Recent] Data and Parse JSON \n
                    combine_file_list()  : Combine all categories of data \n
                    devide_file_list() : Separate files and folders. \n
                    download_thumbnails() : Request a thumbnail for each file. \n
                    run_collector() : Provides various functions to the user. \n

                :return:
                    explore success  --  CA_OK
                    explore fail     --  CA_ERROR
        """
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
                    if page.frame_locator("section[role=\"main\"] iframe").locator(
                            "text=We need a little more help").is_visible():
                        # CATCH select personal default (Changeable)
                        # p_or_b = input(Colors.YELLOW + "[>>] Which Account? Business: 1, Personal: 2  >>" + Colors.RESET)
                        p_or_b = 2
                        if p_or_b == 1:
                            with page.expect_navigation():
                                page.frame_locator("section[role=\"main\"] iframe").locator(
                                    "text=Created by your IT department").click()
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
                if page.query_selector("xpath=//*[@id=\"idDiv_SAOTCS_Title\"]") is None:
                    flag = 0
                else:
                    flag = 1

                if flag == 1:
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
                    title = page.locator("xpath=//*[@id=\"idDiv_SAOTCS_Title\"]").inner_text()
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
                    page.locator("xpath=//*[@id=\"idTxtBx_SAOTCC_OTC\"]").click()
                    page.locator("xpath=//*[@id=\"idTxtBx_SAOTCC_OTC\"]").fill(factor2)
                    page.locator("//*[@id=\"idSubmit_SAOTCC_Continue\"]").click()

                elif page.locator("text=Approve sign in request").is_visible():
                    # App Login
                    PRINTI(page.locator("xpath=//*[@id=\"idDiv_SAOTCAS_Description\"]").text_content())
                    factor2 = input("Please press Enter when approval is completed.")

                with page.expect_navigation():
                    page.locator("text=No").click()
                page.wait_for_timeout(1000)

                while True:
                    self.__caller = page.url[page.url.find("cid=") + 4:]
                    self.__all_cookies = page.context.cookies()

                    page.wait_for_timeout(1000)

                    if self.__set_auth_value() == CA_ERROR:
                        PRINT('Set Authentication Value Error')
                        continue

                    if self.__set_header_value() == CA_ERROR:
                        PRINT('Set Header Value Error')
                        continue

                    if self.__set_vault_name() == CA_ERROR:
                        PRINT('Set Vault Name Error. Please Wait')
                        continue
                    else:
                        break

                PRINT("Personal Vault requires an authentication code. Please enter the following contents.")
                # with page.expect_navigation():
                with page.expect_popup() as popup_info:
                    page.locator("text=" + self.__vault_name).click()
                    page.wait_for_timeout(1000)
                page1 = popup_info.value

                if page1.query_selector("xpath=//*[@id=\"idDiv_SAOTCS_Title\"]") is None:
                    if page1.query_selector("xpath=//*[@id=\"idDiv_SAOTCAS_Description\"]") is None:
                        flag = 0
                    else:
                        flag = 2
                else:
                    flag = 1
                if flag == 1:
                    factor2_texts = page1.locator("div[role=\"button\"]").all_inner_texts()
                    cnt = 1
                    if len(factor2_texts) > 1:
                        for factor2_text in factor2_texts:
                            PRINTI(str(cnt) + '. ' + factor2_text.replace('\n', ''))
                            cnt += 1
                        factor2_cnt = input("What number would you like to use to authenticate? >> ")
                        page1.locator("div[role=\"button\"]").locator(
                            "text =" + factor2_texts[int(factor2_cnt) - 1].replace('\t', '').replace('\n','')).click()
                    else:
                        with page1.expect_navigation():
                            page1.locator("div[role=\"button\"]").click()
                    page1.wait_for_timeout(500)

                    if page1.query_selector("xpath=//*[@id=\"idDiv_SAOTCS_ProofConfirmationDesc\"]") is None:
                        aflag = 0
                    else:
                        aflag = 1
                    if aflag == 1:
                        # SMS
                        PRINTI(page1.locator("xpath=//*[@id=\"idDiv_SAOTCS_ProofConfirmationDesc\"]").text_content())
                        factor2_sms = input("Last 4 digits of phone number >>")
                        page1.locator("xpath=//*[@id=\"idTxtBx_SAOTCS_ProofConfirmation\"]").fill(factor2_sms)
                        page1.locator("xpath=//*[@id=\"idSubmit_SAOTCS_SendCode\"]").click()
                    else:
                        # E-mail
                        PRINTI(page1.locator("xpath=//*[@id=\"idDiv_SAOTCC_Description\"]").text_content())

                    page1.wait_for_timeout(500)
                    factor2 = input("Enter code >>")
                    page1.locator("xpath=//*[@id=\"idTxtBx_SAOTCC_OTC\"]").click()
                    page1.locator("xpath=//*[@id=\"idTxtBx_SAOTCC_OTC\"]").fill(factor2)
                    page1.locator("//*[@id=\"idSubmit_SAOTCC_Continue\"]").click()

                elif flag == 2:
                    # App Login
                    PRINTI(page1.locator("xpath=//*[@id=\"idDiv_SAOTCAS_Description\"]").text_content())
                    factor2 = input("Please press Enter when approval is completed.")



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

                if self.__set_recent_file_list() == CA_ERROR:
                    PRINT('Set Recent File List Error')
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

                if self.__run_collector() == CA_ERROR:
                    return CA_ERROR

                return CA_OK

        except Exception as e:
            PRINTE(e)
            return CA_ERROR

    def __run_collector(self):
        file_len = len(self.__file_list)
        self.__set_show_file_list()
        while True:
            try:
                menu = cd.select_menu()
            except:
                PRINTE("Please Input Correct Number")
                continue
            if menu == 0:  # exit
                break
            elif menu == 1:  # all of file
                try:
                    show_menu = cd.select_show_menu()
                except:
                    PRINTE("Please Input Correct Number")
                    continue
                if show_menu == 0:
                    continue
                elif show_menu == 1:
                    self.show_file_list()
                elif show_menu == 2:
                    self.show_my_files_list()
                elif show_menu == 3:
                    self.show_recent_list()
                elif show_menu == 4:
                    self.show_shared_list()
                elif show_menu == 5:
                    self.show_recycle_list()
            elif menu == 2:  # select file
                self.show_file_list()
                while True:
                    try:
                        download_number = int(input("Put file numbers (exit:0): "))
                        if download_number == 0:
                            break

                        if download_number < 0:
                            print("\n Please put correct number.")
                            continue
                        elif download_number > file_len:
                            print("Please put correct number.")
                            continue
                        self.download_file(download_number)
                    except:
                        PRINTE("Please Input Correct Number")
            elif menu == 3:  # search
                try:
                    sm = cd.search_menu()
                except:
                    PRINTE("Please Input Correct Number")
                    continue
                s_input = CInput()
                if sm == 0:
                    continue
                elif sm == 1:
                    q = input("What do you want to search for? >> ")
                    self.search_file(q)
                elif sm == 2:
                    search_period = s_input.set_m_period()
                    if search_period[0] and search_period[1]:
                        if search_period[0] != '1970-01-01':
                            re_start_time = datetime.datetime.strptime(search_period[0],
                                                                       "%Y-%m-%d") - datetime.timedelta(days=1)
                            re_start_time = re_start_time.strftime("%Y-%m-%d")
                        else:
                            re_start_time = search_period[0]
                        s_period = re_start_time
                        e_period = datetime.datetime.strptime(search_period[1],
                                                              "%Y-%m-%d") - datetime.timedelta(days=1)
                        e_period = e_period.strftime("%Y-%m-%d")
                        self.search_file_by_date(s_period, e_period)
                elif sm == 3:
                    q = input("What username do yo want >> ")
                    self.search_file_by_name(q)
            else:
                print(" [!] Invalid Menu. Choose Again.")
                continue
        return CA_OK

    def search_file_by_name(self, q):
        """
            .. note::  User Name is searched using metadata. \n

            :param str q: Name of the user you want to search for
        """
        search_result = []
        name = q

        for file in self.__file_list:
            if name in file['ownerName']:
                search_result.append(file)

        return self.show_file_list_local(search_result, "SEARCH")

    def search_file_by_date(self, start, end):
        """
            .. note::  Data in a specific period is searched using metadata. \n

            :param str start: start date
            :param str end: end date
        """
        search_result = []
        s_time = datetime.datetime.strptime(start, "%Y-%m-%d")
        e_time = datetime.datetime.strptime(end, "%Y-%m-%d")

        for file in self.__file_list:
            try:
                c_time = datetime.datetime.strptime(file['displayCreationDate'], "%Y-%m-%d")
                m_time = datetime.datetime.strptime(file['displayModifiedDate'], "%Y-%m-%d")
            except:
                c_time = datetime.datetime.strptime(file['displayCreationDate'], "%m/%d/%Y")
                m_time = datetime.datetime.strptime(file['displayModifiedDate'], "%m/%d/%Y")

            if s_time <= c_time and c_time <= e_time:
                search_result.append(file)
                continue
            elif s_time <= m_time and m_time <= e_time:
                search_result.append(file)
                continue

        return self.show_file_list_local(search_result, "SEARCH")

    def show_file_list_local(self, file_folder_list, type):
        """
            .. note::  Desired file list is changed to a predetermined output form and output. \n

            :param list file_folder_list: Desired file list
            :param str type: file list type

            :return:
                print file and folder list
        """
        result = list()
        result.append(['file name', 'size(bytes)', 'mimeType', 'createdTime(UTC+9)', 'modifiedTime(UTC+9)', 'file id',
                       'personal?', 'downloadURL'])

        folder_list , file_list = self.devide_file_list_local(file_folder_list)

        for fol in folder_list:
            ticks = fol['creationDate']
            converted_ticks = datetime.datetime(1, 1, 1, 9) + datetime.timedelta(microseconds=ticks / 10)
            converted_ticks.strftime("%Y-%m-%d %H:%M:%S")
            ticks_modi = fol['modifiedDate']
            converted_ticks_modi = datetime.datetime(1, 1, 1, 9) + datetime.timedelta(microseconds=ticks_modi / 10)
            converted_ticks_modi.strftime("%Y-%m-%d %H:%M:%S")

            if fol.get('vault') == None:
                result.append([fol['name'], fol['size'], 'folder', converted_ticks,
                               converted_ticks_modi,
                               fol['id'], 'No', "None"])

            else:
                result.append([fol['name'], fol['size'], 'folder', converted_ticks,
                               converted_ticks_modi,
                               fol['id'], 'Yes', "None"])

        for file in file_list:
            ticks = file['creationDate']
            converted_ticks = datetime.datetime(1, 1, 1, 9) + datetime.timedelta(microseconds=ticks / 10)
            converted_ticks.strftime("%Y-%m-%d %H:%M:%S")
            ticks_modi = file['modifiedDate']
            converted_ticks_modi = datetime.datetime(1, 1, 1, 9) + datetime.timedelta(microseconds=ticks_modi / 10)
            converted_ticks_modi.strftime("%Y-%m-%d %H:%M:%S")

            if file.get('vault') == None:
                result.append([file['name'] + file['extension'], file['size'], file['mimeType'], converted_ticks,
                               converted_ticks_modi,
                               file['id'], 'False', file['urls']['download']])
            else:
                result.append(
                    [file['name'] + file['extension'], file['size'], file['mimeType'], converted_ticks,
                     converted_ticks_modi, file['id'],
                     'True', file['urls']['download']])

        cnt = 0
        new_list = [result[0]]

        file_count = len(result)
        if file_count == 0:
            print("No FILE.")
            return None
        print("\n")

        for file in result:
            if cnt == 0:
                cnt = 1
                continue

            name = file[0]
            mtype = file[2]

            if len(name) >= 20:
                name = name[0:8] + '....' + name[-6:]
            if len(mtype) >= 20:
                mtype = mtype[0:8] + '....' + mtype[-6:]

            new_list.append([name, file[1], mtype, file[3], file[4], file[5], file[6], file[7]])
        file_count = len(result)
        if file_count == 0:
            PRINTI("No FILE.")
            return None
        print("\n")

        print("======" + type + "_FILE_LIST======")
        print("FILE_COUNT:" + str(file_count - 1))
        print(tabulate.tabulate(new_list, headers="firstrow", tablefmt='github', showindex=range(1, file_count),
                                numalign="left"))

    def search_file(self, q):
        """
            .. note::  String search using Request URL. \n

            :param str q: String you want to search for
        """
        search_result = []
        search_response = self.__request_search_file(q)
        if search_response['items'][0]['folder']['childCount'] == 0:
            print("No Items.")
        else:
            for child in search_response['items'][0]['folder']['children']:
                search_result.append(child)

        self.show_file_list_local(search_result, "SEARCH")

    def __request_search_file(self, q):
        cookies = {
            'WLSSC': self.__cookie_wlssc,
        }

        headers = {
            'Host': 'skyapi.onedrive.live.com',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.151 Whale/3.14.134.62 Safari/537.36',
            'canary': self.__header_canary,
            'Accept': 'application/json',
            'AppId': '1141147648',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        params = {
            'caller': self.__caller,
            'ps': '50',
            'd': '1',
            'includeSharedItems': '1',
            'id': 'root',
            'cid': self.__cid,
            'qt': 'search',
            'q': q,
        }

        response = requests.get('https://skyapi.onedrive.live.com/API/2/GetItems', params=params, headers=headers,
                                cookies=cookies,
                                verify=False)

        return json.loads(response.text)

    def download_file(self, file_num):
        """
            .. note::  Functions that request to download the selected file \n
                       (using Download URL)

            :param int file_num: Selected file index
        """
        download_url = self.__show_file_list[file_num][8]
        file_name = self.__show_file_list[file_num][0]

        if download_url == "None":
            PRINTI("Folder cannot be downloaded")
            return

        host = download_url[download_url.find(r'//') + 2:download_url.find("com/") + 3]
        headers = {
            'Host': host,
            'Accept': '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'navigate',
            'Referer': 'https://onedrive.live.com/',
            'Accept-Encoding': 'deflate, br',
        }

        response = requests.get(
            download_url,
            headers=headers, verify=False, allow_redirects=False)

        if response.status_code == 200:
            #
            if not (os.path.isdir('./download')):
                os.makedirs('./download')

            with open('./download/' + file_name, 'wb') as a:
                a.write(response.content)

            PRINTI("Download " + file_name + " Done")
        else:
            print("[!] Download_error!")
            print("[!] Please click 'downloadURL' for download file!")

    def show_file_list(self):
        """
            .. note::  Show all file and folder stored on OneDrive \n
        """
        cnt = 0
        new_list = []
        new_list = [self.__show_file_list[0]]
        file_count = len(self.__show_file_list)
        if file_count == 0:
            print("No FILE.")
            return None
        print("\n")

        for file in self.__show_file_list:
            if cnt == 0:
                cnt = 1
                continue

            name = file[0]
            mtype = file[2]

            if len(name) >= 20:
                name = name[0:8] + '....' + name[-6:]
            if len(mtype) >= 20:
                mtype = mtype[0:8] + '....' + mtype[-6:]

            new_list.append([name, file[1], mtype, file[3], file[4], file[5], file[6], file[7], file[8]])

        print("======DRIVE_FILE_LIST======")
        print("FILE_COUNT:" + str(file_count - 1))
        print(tabulate.tabulate(new_list, headers="firstrow", tablefmt='github', showindex=range(1, file_count),
                                numalign="left"))

    def __set_show_file_list(self):
        """
            .. note::  Only meaningful metadata is selected and normalized from all data. \n
        """
        result = list()
        # Select the desired metadata.
        result.append(['file name', 'size(bytes)', 'mimeType', 'createdTime(UTC+9)', 'modifiedTime(UTC+9)', 'file id',
                       'personal?', 'Deleted?', 'downloadURL'])
        for fol in self.__folder_list:
            ticks = fol['creationDate']
            converted_ticks = datetime.datetime(1, 1, 1, 9) + datetime.timedelta(microseconds=ticks / 10)
            converted_ticks.strftime("%Y-%m-%d %H:%M:%S")
            ticks_modi = fol['modifiedDate']
            converted_ticks_modi = datetime.datetime(1, 1, 1, 9) + datetime.timedelta(microseconds=ticks_modi / 10)
            converted_ticks_modi.strftime("%Y-%m-%d %H:%M:%S")

            if fol.get('vault') == None:
                if fol.get('isRecycled') == None:
                    result.append([fol['name'], fol['size'], 'folder', converted_ticks,
                                   converted_ticks_modi,
                                   fol['id'], 'No', 'No', "None"])
                else:
                    result.append([fol['name'], fol['size'], 'folder', converted_ticks,
                                   converted_ticks_modi,
                                   fol['id'], 'No', 'Yes', "None"])
            else:
                result.append([fol['name'], fol['size'], 'folder', converted_ticks,
                               converted_ticks_modi,
                               fol['id'], 'Yes', 'No', "None"])

        for file in self.__file_list:
            ticks = file['creationDate']
            converted_ticks = datetime.datetime(1, 1, 1, 9) + datetime.timedelta(microseconds=ticks / 10)
            converted_ticks.strftime("%Y-%m-%d %H:%M:%S")
            ticks_modi = file['modifiedDate']
            converted_ticks_modi = datetime.datetime(1, 1, 1, 9) + datetime.timedelta(microseconds=ticks_modi / 10)
            converted_ticks_modi.strftime("%Y-%m-%d %H:%M:%S")

            if file.get('vault') == None:
                if file.get('isRecycled') == None:
                    result.append([file['name'] + file['extension'], file['size'], file['mimeType'], converted_ticks,
                                   converted_ticks_modi,
                                   file['id'], 'No', 'No', file['urls']['download']])
                else:
                    result.append([file['name'] + file['extension'], file['size'], file['mimeType'], converted_ticks,
                                   converted_ticks_modi,
                                   file['id'], 'No', 'Yes', file['urls']['download']])
            else:
                result.append(
                    [file['name'] + file['extension'], file['size'], file['mimeType'], converted_ticks,
                     converted_ticks_modi, file['id'],
                     'Yes', 'No', file['urls']['download']])

        self.__show_file_list = result

    def __set_auth_value(self):
        """
            .. note:: Collect essential values(Cookie: WLSSC, msa_auth)
        """
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
            .. note:: Collect essential values using Request(Header value: Canary)
                      Need to read javascript(response)
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

    def __set_vault_name(self):
        try:
            file_list = self.__request_file_list()

            root_folder = file_list['items'][0]['folder']
            children = root_folder['children']

            if file_list['items'][0]['id'] == 'root':
                for child in children:
                    if child.get('vault') is not None:
                        self.__vault_name = child['name']
                        return CA_OK

        except Exception as e:
            return CA_ERROR
        return CA_OK

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

    def __set_recent_file_list(self):
        try:
            file_list = self.__request_file_list(qt='mru')
            self.__recent_file_list = self.__remake_file_list(file_list, 'root', self.__recent_file_list, qt='mru')
            self.__flag = 0
            self.__number_of_recent_file = len(self.__recent_file_list)
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
        # make Json
        if qt == 'recyclebin':
            name_id = 'recyclebin'
        elif qt == 'sharedby':
            name_id = 'sharedby'
        elif qt == 'mru':
            name_id = 'recent'
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
                    if child.get('vault') is not None and self.__flag == 0:
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
        self.__total_file_count = self.__number_of_normal_file + self.__number_of_recycle_file + self.__number_of_shared_file + self.__number_of_recent_file
        self.__total_file_list = self.__normal_file_list + self.__recycle_file_list + self.__shared_file_list + self.__recent_file_list

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

    @staticmethod
    def devide_file_list_local(file_folder_list):
        folder_list = []
        file_list = []
        for file in file_folder_list:
            if 'folder' in file:
                folder_list.append(file)
            else:
                file_list.append(file)

        return folder_list, file_list

    def show_my_files_list(self):
        return self.show_file_list_local(self.__normal_file_list, "MY_FILE")

    def show_recent_list(self):
        return self.show_file_list_local(self.__recent_file_list, "RECENT")

    def show_shared_list(self):
        return self.show_file_list_local(self.__shared_file_list, "SHARED")

    def show_recycle_list(self):
        return self.show_file_list_local(self.__recycle_file_list,"RECYCLE_BIN")