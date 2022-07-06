"""
============================================
    "explorer" Module
============================================
.. moduleauthor:: Jihyeok Yang <piki@korea.ac.kr>

.. note::
    'TITLE'             : OneDrive - Explorer in CATCH\n
    'AUTHOR'            : Jihyeok Yang\n
    'TEAM'              : DFRC\n
    'VERSION'           : 0.0.4\n
    'RELEASE-DATE'      : 2022-05-18\n

--------------------------------------------

Description
===========

    OneDrive Internal APIs 를 사용해서 OneDrive에 저장된 데이터 파싱하는 모듈

    도구이름    : Cloud Data Acquisition through Comprehensive and Hybrid Approaches(CATCH)\n
    프로젝트    : Cloud Data Acquisition through Comprehensive and Hybrid Approaches\n
    연구기관    : 고려대학교(Korea Univ.)\n

History
===========

    * 2022-05-18 : 초기 버전
    * 2022-05-27 : 썸네일 다운로드
    * 2022-06-05 : 파일 버전 획득

"""

from onedrive_collector.authenticator import *
from tqdm import tqdm

class Exploration:

    def __init__(self, auth_data):
        """
            :param list auth_data: auth_data from authenticator.py
        """
        self.__auth_data = auth_data
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
        self.__flag = 0
        self.__file_list = []
        self.__folder_list = []

    def run(self):
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

        # if self.__download_thumbnails() == CA_ERROR:
        #     PRINT('Collecting Thumbnails Error')
        #     return CA_ERROR
        #
        # if self.__set_version_history() == CA_ERROR:
        #     return CA_ERROR

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
            'WLSSC': self.__auth_data.get_cookie_wlssc(),
        }

        headers = {
            'Host': 'skyapi.onedrive.live.com',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'canary': self.__auth_data.get_header_canary(),
            'Accept': 'application/json',
            'AppId': '1141147648',
            'Accept-Encoding': 'deflate, br',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        if qt == '':
            params = (
                ('caller', self.__auth_data.get_parameter_caller()),
                ('d', '1'),
                ('id', id),
                ('cid', self.__auth_data.get_parameter_cid()),
                ('ps', 2000)
            )
        else:
            params = (
                ('caller', self.__auth_data.get_parameter_caller()),
                ('d', '1'),
                ('id', id),
                ('cid', self.__auth_data.get_parameter_cid()),
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

        request_url = 'https://api.onedrive.com/v1.0/drive/items/' + file_num + '/versions?access_token=' + self.__auth_data.get_cookie_msa_auth()

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