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

    Modules that use OneDrive Internal APIs to provide the desired functionality

    Tool        : Cloud Data Acquisition through Comprehensive and Hybrid Approaches(CATCH)\n
    Project     : Cloud Data Acquisition through Comprehensive and Hybrid Approaches\n
    Research    : Korea Univ. Digital Forensic Research Center(DFRC)\n

History
===========

    * 2022-05-18 : 1st Version
    * 2022-05-25 : Add Show File List
    * 2022-06-05 : Add Search Function (query using Internal API)
    * 2022-06-16 : Add Download Function
    * 2022-06-23 : Add Search by Period (query using Metadata)

"""

from onedrive_collector.onedrive_internal.explorer import *

class Collector:
    """Collector Class

        .. note::  Provides various functions to the user.
                 Function   --  Download
                            --  String Search
                            --  Period Search
                            --  User Name Search
    """
    def __init__(self, onedrive_data, auth_data):
        """
            :param class auth_data: auth_data from authenticator.py
            :param class onedrive_data: Data stored in OneDrive from explorer.py
        """
        self.__onedrive = onedrive_data
        self.__auth_data = auth_data
        self.__total_file_list, self.__file_list, self.__folder_list = self.__onedrive.get_total_file_list()
        self.__re_file_list = None

    def get_num_of_file_list(self):
        return len(self.__total_file_list)

    def download_file(self, file_num):
        """
            .. note::  Functions that request to download the selected file \n
                       (using Download URL)

            :param int file_num: Selected file index
        """
        download_url = self.__re_file_list[file_num][8]
        file_name = self.__re_file_list[file_num][0]

        # Folder is not File
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
            # Sometimes it doesn't work --> Click downloadURL link
            print("[!] Download_error!")
            print("[!] Please click 'downloadURL' for download file!")

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

    def show_file_list(self):
        """
            .. note::  Show all file and folder stored on OneDrive \n
        """
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

            new_list.append([name, file[1], mtype, file[3], file[4], file[5], file[6], file[7], file[8]])

        print("======DRIVE_FILE_LIST======")
        print("FILE_COUNT:" + str(file_count - 1))
        print(tabulate.tabulate(new_list, headers="firstrow", tablefmt='github', showindex=range(1, file_count),
                                numalign="left"))

    def set_file_list(self):
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

        self.__re_file_list = result

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

        folder_list, file_list = self.__onedrive.devide_file_list_local(file_folder_list)

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
                               file['id'], 'NO', file['urls']['download']])
            else:
                result.append(
                    [file['name'] + file['extension'], file['size'], file['mimeType'], converted_ticks,
                     converted_ticks_modi, file['id'],
                     'YES', file['urls']['download']])

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

            # If the name is more than 20 characters, it implies.
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

        print("======"+type+"_FILE_LIST======")
        print("FILE_COUNT:" + str(file_count - 1))
        print(tabulate.tabulate(new_list, headers="firstrow", tablefmt='github', showindex=range(1, file_count),
                                numalign="left"))

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

        self.show_file_list_local(search_result, 'SEARCH')

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

        if response.status_code == 404:
            PRINTE("The API may have changed.")
            return CA_ERROR

        return json.loads(response.text)

    def show_my_files_list(self):
        return self.show_file_list_local(self.__onedrive.get_my_files(), "MY_FILE")

    def show_recent_list(self):
        return self.show_file_list_local(self.__onedrive.get_recent(), "RECENT")

    def show_shared_list(self):
        return self.show_file_list_local(self.__onedrive.get_shared(), "SHARED")

    def show_recycle_list(self):
        return self.show_file_list_local(self.__onedrive.get_recycle(),"RECYCLE_BIN")

