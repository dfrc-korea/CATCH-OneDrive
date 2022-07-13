'''
    ONEDRIVE API
'''

from __future__ import unicode_literals

from module.CATCH_Cloud_Define import *
import module.Cloud_Display as cd
from tqdm import tqdm


class OneDrive:
    def __init__(self, redirect_uri, client_secret, client_id):
        self.__access_token = None
        self.extract_path = "./"
        self.__redirect_uri = redirect_uri
        self.__client_secret = client_secret
        self.__client_id = client_id
        self.__auth_code = None
        self.__auth_url = None
        self.__client = None
        self.__folder_list = []
        self.__file_list = []
        self.__shared_file_list = []
        self.__default_file_list = []
        self.__item_id = "root"
        self.__file_count = None
        self.__session = None
        self.__refresh_token = None
        self.__identity = None

    def run(self):
        PRINTI("Start OneDrive Module - <Open Mode>")

        if self.__set_client_by_account() == CA_ERROR:
            PRINTE("Set Client Error")
            return CA_ERROR

        if self.__set_items() == CA_ERROR:
            PRINTE("Set Item Error")
            return False

        if self.__run_collector() == CA_ERROR:
            PRINTE("Collector Error")
            return CA_ERROR

        return CA_OK

    def show_file_list(self):
        """
            .. note::  Show all file and folder stored on OneDrive \n
        """
        new_list = []
        for id, file, f, created_time, modified_time, size, path in self.__file_list:
            if created_time is None:
                created_time = '-'
            elif type(created_time) == datetime.datetime:
                created_time = created_time + datetime.timedelta(hours=9)

            if modified_time is None:
                modified_time = '-'
            elif type(modified_time) == datetime.datetime:
                modified_time = modified_time + datetime.timedelta(hours=9)

            if path is None:
                path = '-'

            new_list.append([file, f, created_time, modified_time, size, path])
        print('======ONEDRIVE_FILE_LIST======')
        print('FILE_COUNT:', len(self.__file_list) - 1)
        print(tabulate.tabulate(new_list, headers="firstrow", tablefmt='github', showindex=range(1, len(self.__file_list)),
                                numalign="left"))

    def show_recent_list(self):
        # Recent REST API will Update
        # endpoint = "https://api.onedrive.com/v1.0/drive/recent"
        # headers = {"Authorization": "Bearer " + self.__access_token}
        # response = requests.get(endpoint, headers=headers).json()
        PRINTI("Recent REST API will be update")

    def show_recycle_list(self):
        PRINTI("The open api does not support Recycle Bin.")

    def show_shared_list(self):
        new_list = []
        for id, file, f, created_time, modified_time, size, path in self.__shared_file_list:
            if created_time is None:
                created_time = '-'
            elif type(created_time) == datetime.datetime:
                created_time = created_time + datetime.timedelta(hours=9)

            if modified_time is None:
                modified_time = '-'
            elif type(modified_time) == datetime.datetime:
                modified_time = modified_time + datetime.timedelta(hours=9)

            if path is None:
                path = '-'

            new_list.append([file, f, created_time, modified_time, size, path])
        print('======ONEDRIVE_FILE_LIST======')
        print('FILE_COUNT:', len(self.__shared_file_list) - 1)
        print(tabulate.tabulate(new_list, headers="firstrow", tablefmt='github',
                                showindex=range(1, len(self.__shared_file_list)),
                                numalign="left"))

    def __run_collector(self):
        file_len = len(self.__file_list)
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
                    self.show_file_list()
                elif show_menu == 3:
                    self.show_recent_list()
                elif show_menu == 4:
                    self.show_shared_list()
                elif show_menu == 5:
                    self.show_recycle_list()
            elif menu == 2:  # Download file
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
                        self.download_file(self.__file_list[download_number])
                    except:
                        PRINTE("Please Input Correct Number")

            elif menu == 3:   # search
                q = input("What do you want to search for? >> ")
                self.search_file(q)
            else:
                print(" [!] Invalid Menu. Choose Again.")
                continue

        return CA_OK

    def __item_search(self, q):
        file_list = []
        collection_page = self.__client.item(drive='me', id='root').search(q).get()
        for item in collection_page:
            if item.file == None:
                f = 'Folder'
            else:
                f = 'File'
            if item.name == 'root' or item.size == 0:
                if item.name == 'root':
                    file_list.append(
                        [item.id, item.name, f, '-', item.last_modified_date_time, item.size, 'root'])
                else:
                    file_list.append([item.id, item.name, f, '-', item.last_modified_date_time, item.size, None])
            else:
                file_list.append(
                    [item.id, item.name, f, item.created_date_time, item.last_modified_date_time, item.size,
                     item.parent_reference.path])
        if len(file_list) == 0:
            PRINTI("No File.")
            return
        self.show_file_list_local(file_list)

    def show_file_list_local(self, file_list):
        """
            .. note::  Show all file and folder stored on OneDrive \n
        """
        new_list = []
        for id, file, f, created_time, modified_time, size, path in file_list:
            if created_time is None:
                created_time = '-'
            elif type(created_time) == datetime.datetime:
                created_time = created_time + datetime.timedelta(hours=9)

            if modified_time is None:
                modified_time = '-'
            elif type(modified_time) == datetime.datetime:
                modified_time = modified_time + datetime.timedelta(hours=9)

            if path is None:
                path = '-'

            new_list.append([file, f, created_time, modified_time, size, path])
        print('======ONEDRIVE_FILE_LIST======')
        print('FILE_COUNT:', len(file_list) - 1)
        print(tabulate.tabulate(new_list, headers="firstrow", tablefmt='github', showindex=range(1, len(file_list)),
                                numalign="left"))

    def search_file(self, query):
        self.__item_search(query)

    def __set_client_by_account(self) -> bool:
        try:
            scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readonly']

            self.__client = onedrivesdk.get_default_client(client_id=self.__client_id, scopes=scopes)
            self.__auth_url = self.__client.auth_provider.get_auth_url(self.__redirect_uri)
            # Block thread until we have the code
            self.__auth_code = GetAuthCodeServer.get_auth_code(self.__auth_url, self.__redirect_uri)
            # Finally, authenticate!
            self.__client.auth_provider.authenticate(self.__auth_code, self.__redirect_uri, self.__client_secret)

            self.__parse_session()
        except:
            return CA_ERROR
        return CA_OK

    def __parse_session(self):
        # a = self.__client._session
        self.__access_token = 'need update'
        self.__refresh_token = 'need update'

    def __navigate(self):
        items = self.__client.item(id=self.__item_id).children.get()
        return items

    def __list_changes(self, token):
        """Get Item list in OneDrive\n
            .. note:: 리스팅을 하는 작업을 직접하는데 각각 내부의 요소가 존재\n
            item{
                created_by: IdentitySet(class) -> createdBy\n
                created_date_time: createdDataTime(dateTime)\n
                c_tag: cTage\n
                description: description\n
                e_tag: eTag\n
                id: id\n
                last_modified_by: IdentitySet(class) -> lastModifiedBy\n
                last_modified_date_time: lastModifiedDateTime(dateTime)\n
                name: name\n
                parent_reference: ItemReference(class) -> parentReference\n
                size: size(int)\n
                web_url: webUrl\n
                audio: Audio(class) -> audio\n
                deleted: Deleted(class) -> deleted\n
                file: File(class) -> file\n
                file_system_info: FileSystemInfo(class) -> fileSystemInfo\n
                folder: Folder(class) -> folder\n
                image: Image(class) -> image\n
                location: Location(class) -> location\n
                open_with: OpenWithSet(class) -> openWith\n
                photo: Photo(class) -> photo\n
                remote_item: Item(class) -> remoteItem\n
                search_result: SearchResult(class) -> searchResult\n
                shared: Shared(class) -> shared\n
                special_folder: SpecialFolder(class) -> specialFolder\n
                video: Video(class) -> video\n
                permissions: PermissionsCollectionPage(class) -> permissions\n
                subscriptions: SubscriptionsCollectionPage(class) -> subscriptions\n
                versions: VersionsCollectionPage(class) -> versions\n
                children: ChildrenCollectionPage(class) -> children\n
                tags: TagsCollectionPage(class) -> tags\n
                thumbnails: ThumbnailsCollectionPage(class) -> thumbnails\n
            }
            :param token: None
            :return: None
        """
        collection_page = self.__client.item(id=self.__item_id).delta(token).get()

        # Will Update using REST API
        # endpoint = "https://api.onedrive.com/v1.0/drives/me/drive/activities"
        # headers = {"Authorization": "Bearer " + self.__access_token}
        # response = requests.get(endpoint, headers=headers).json()

        self.__file_list.append(['id', 'file name', 'type', 'createdTime(+09:00)', 'modifiedTime(+09:00)', 'size', 'path'])
        self.__shared_file_list.append(
            ['id', 'file name', 'type', 'createdTime(+09:00)', 'modifiedTime(+09:00)', 'size', 'path'])

        for item in collection_page:
            if item.file == None:
                f = 'Folder'
            else:
                f = 'File'
            if item.shared != None:
                self.__shared_file_list.append([item.id, item.name, f, item.created_date_time, item.last_modified_date_time, item.size, item.parent_reference.path])
            if item.name == 'root' or item.size == 0:
                if item.name == 'root':
                    self.__file_list.append([item.id, item.name, f, '-', item.last_modified_date_time, item.size, 'root'])
                else:
                    self.__file_list.append([item.id, item.name, f, '-', item.last_modified_date_time, item.size, None])
            else:
                self.__file_list.append([item.id, item.name, f, item.created_date_time, item.last_modified_date_time, item.size, item.parent_reference.path])

    def __set_items(self):
        try:
            token = None
            items = self.__navigate()

            for count, item in enumerate(items):
                self.__folder_list.append([item.id, item.name])

            self.__list_changes(token)
            self.__default_file_list = self.__file_list

            self.__download_thumbnails()
        except:
            return CA_ERROR
        return CA_OK

    def get__folder_list(self):
        return self.__folder_list

    def get_members(self):
        member = dict()
        member['access_token'] = self.__access_token
        member['redirect_uri'] = self.__redirect_uri
        member['client_secret'] = self.__client_secret
        member['client_id'] = self.__client_id
        member['auth_code'] = self.__auth_code
        member['auth_url'] = self.__auth_url
        member['refresh_token'] = self.__refresh_token
        print("[+] Collect member list Done!")

        return member

    def get__file_list(self):
        return self.__file_list

    def download_file(self, file):
        if not (os.path.isdir('./download')):
            os.makedirs('./download')
        try:
            self.__client.item(drive='me', id=file[0]).download("./download/"+file[1])
            PRINTI("Download " + file[1] + " Done")
        except:
            print("[!] Download_error!")

    def __download_thumbnail(self, file_id, file_name):
        self.__client.item(id=file_id).thumbnails[0].medium.download("./thumbnails/" + str(file_name) + ".jpg")

    def __download_thumbnails(self):
        for file in tqdm(self.__default_file_list[1:]):
            try:
                if "thumbnail" in file[1]:
                    self.__download_thumbnail(file[0], file[1])
                else:
                    continue
            except Exception as e:
                pass