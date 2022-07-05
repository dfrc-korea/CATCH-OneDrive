"""
============================================
    "collector" Module
============================================
.. moduleauthor:: Jihyeok Yang <piki@korea.ac.kr>

.. note::
    'TITLE'             : OneDrive - Collector in CATCH\n
    'AUTHOR'            : Jihyeok Yang\n
    'TEAM'              : DFRC\n
    'VERSION'           : 0.0.4\n
    'RELEASE-DATE'      : 2022-05-18\n

--------------------------------------------

Description
===========

    OneDrive Internal APIs 를 사용해서 원하는 기능을 제공하는 모듈

    도구이름    : Cloud Data Acquisition through Comprehensive and Hybrid Approaches(CATCH)\n
    프로젝트    : Cloud Data Acquisition through Comprehensive and Hybrid Approaches\n
    연구기관    : 고려대학교(Korea Univ.)\n

History
===========

    * 2022-05-18 : 초기 버전 - 생성
    * 2022-05-25 : 파일 목록 추가
    * 2022-06-05 : 검색 기능 추가 (query using Internal API)
    * 2022-06-16 : 다운로드 기능 추가
    * 2022-06-23 : 기간 별 검색 기능 추가 (query using Metadata)

    * 해야할 일들 : 휴지통 다운로드... 분석 및 구현....

"""

from onedrive_collector.explorer import *
from onedrive_collector.PV_authenticator_and_explorer import *

class Collector:
    def __init__(self, onedrive_data, auth_data):
        self.__onedrive = onedrive_data
        self.__auth_data = auth_data
        self.__total_file_list, self.__file_list, self.__folder_list = self.__onedrive.get_total_file_list()
        self.__re_file_list = None

    def get_num_of_file_list(self):
        return len(self.__total_file_list)

    def download_file(self, file_num):
        download_url = self.__re_file_list[file_num][7]
        file_name = self.__re_file_list[file_num][0]

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

    def search_file_by_date(self, start, end):
        search_result = []
        s_time = datetime.datetime.strptime(start, "%Y-%m-%d")
        e_time = datetime.datetime.strptime(end, "%Y-%m-%d")

        for file in self.__file_list:
            c_time = datetime.datetime.strptime(file['displayCreationDate'], "%Y-%m-%d")
            m_time = datetime.datetime.strptime(file['displayModifiedDate'], "%Y-%m-%d")

            if s_time <= c_time and c_time <= e_time:
                search_result.append(file)
                continue
            elif s_time <= m_time and m_time <= e_time:
                search_result.append(file)
                continue

        return self.show_file_list_local(search_result)

    def show_file_list(self):
        cnt = 0
        new_list = []
        new_list = [self.__re_file_list[0]]
        file_count = len(self.__re_file_list)
        if file_count == 0:
            print("No FILE.")
            return None
        print("\n")

        for file in self.__re_file_list:
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

        print("======DRIVE_FILE_LIST======")
        print("FILE_COUNT:" + str(file_count - 1))
        print(tabulate.tabulate(new_list, headers="firstrow", tablefmt='github', showindex=range(1, file_count),
                                numalign="left"))

    def set_file_list(self):
        result = list()
        result.append(['file name', 'size(bytes)', 'mimeType', 'createdTime(UTC+9)', 'modifiedTime(UTC+9)', 'file id',
                       'personal?', 'downloadURL'])
        for file in self.__file_list:
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

        self.__re_file_list = result

    @staticmethod
    def show_file_list_local(file_list):
        """Search 결과 출력 메소드

                        .. note::  일반 출력과 다르게 검색된 결과만 출력 \n

                        :return:
                            no file     --  None
                            file exist  --  File list
                """
        result = list()
        result.append(['file name', 'size(bytes)', 'mimeType', 'createdTime(UTC+9)', 'modifiedTime(UTC+9)', 'file id',
                       'personal?', 'downloadURL'])
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

        print("======DRIVE_FILE_LIST======")
        print("FILE_COUNT:" + str(file_count - 1))
        print(tabulate.tabulate(new_list, headers="firstrow", tablefmt='github', showindex=range(1, file_count),
                                numalign="left"))

    def search_file_by_name(self, q):
        search_result = []
        name = q

        for file in self.__file_list:
            if name in file['ownerName']:
                search_result.append(file)

        return self.show_file_list_local(search_result)


    def search_file(self, q):
        search_result = []
        search_response = self.__request_search_file(q)
        if search_response['items'][0]['folder']['childCount'] == 0:
            print("No Items.")
        else:
            for child in search_response['items'][0]['folder']['children']:
                search_result.append(child)

        self.show_file_list_local(search_result)

    def __request_search_file(self, q):
        cookies = {
            'WLSSC': self.__auth_data.get_cookie_wlssc(),
        }

        headers = {
            'Host': 'skyapi.onedrive.live.com',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.151 Whale/3.14.134.62 Safari/537.36',
            'canary': self.__auth_data.get_header_canary(),
            'Accept': 'application/json',
            'AppId': '1141147648',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        params = {
            'caller': self.__auth_data.get_parameter_caller(),
            'ps': '50',
            'd': '1',
            'includeSharedItems': '1',
            'id': 'root',
            'cid': self.__auth_data.get_parameter_cid(),
            'qt': 'search',
            'q': q,
        }

        response = requests.get('https://skyapi.onedrive.live.com/API/2/GetItems', params=params, headers=headers, cookies=cookies,
                                verify=False)

        ## 검색 결과 디버깅
        # if not (os.path.isdir('./search_results')):
        #     os.makedirs('./search_results')
        #
        # with open('.//search_results/search_' + q + '.json', 'w', encoding='utf-8') as make_file:
        #     json.dump(json.loads(response.text), make_file, ensure_ascii=False, indent='\t')
        # PRINT('Extract json file done. >> search_' + q + '.json')

        return json.loads(response.text)
