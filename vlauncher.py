import json
import os
import requests
import zipfile
import io


class Main:
    def __init__(self, version_provider, downloaded_versions, use_version):
        self.version_provider = version_provider  # a link to server.json
        self.use_version = use_version

        # {version: {"main": "main.py"}}
        self.downloaded_versions = downloaded_versions
        self.downloadable_versions = {}  # {version: download_link}

    def get_downloadable_versions(self):
        if "https" not in self.version_provider[:5]:
            print("Using local version provider")
            with open(self.version_provider) as f:
                self.downloadable_versions = json.load(f).get("versions")
        else:
            print("Using online version provider")
            response = requests.get(self.version_provider)
            print(response)
            self.downloadable_versions = response.json().get("versions")

    def download_version(self, version):
        print(version)
        link = self.downloadable_versions.get(version).get("download")
        print(link)
        if "https" not in link[:5]:
            print("Downloading local version...")
            with zipfile.ZipFile(link, "r") as zip:
                print("Extracting...")
                zip.extractall()  # path?

        else:
            print("Downloading from internet")
            response = requests.get(link)
            in_memory = io.BytesIO(response.content)
            archive = zipfile.ZipFile(in_memory, "r")
            print("Extracting...")
            archive.extractall()

        # update changes to self
        app_main = self.downloadable_versions.get(version).get("main")
        self.downloaded_versions.update({version: {"main": app_main}})

    def launch(self, version):
        run = self.downloaded_versions.get(version)
        os.system("python3 " + version + "/" + run.get("main"))

    def update_state(self):
        config = {
            "version_provider": self.version_provider,
            "downloaded_versions": self.downloaded_versions,
            "use_version": self.use_version
        }
        with open("client.json", "w") as f:
            f.write(json.dumps(config, indent=4))

    def main(self):
        print("Launcher started!")
        self.get_downloadable_versions()
        print(self.downloadable_versions)
        if self.use_version == "latest":
            print("Latest version?")
            if self.downloaded_versions:
                if self.downloadable_versions:
                    # compare versions, download only if not actual latest
                    latest_local = list(
                        sorted(self.downloaded_versions.keys()))[-1]
                    latest_online = list(sorted(
                        self.downloadable_versions.keys()))[-1]
                    print("LATEST LOCAL", latest_local)
                    print("LATEST ONLINE", latest_online)
                    if latest_local == latest_online:
                        # LOCAL
                        print("You have the latest version")
                        self.launch(latest_local)
                    else:
                        # DOWNLOAD
                        print("A new version is available! Downloading...")
                        self.download_version(latest_online)
                        self.launch(latest_online)

                else:
                    print("Unable to check for newer versions")
                    # LOCAL
                    latest_local = list(
                        sorted(self.downloaded_versions.keys()))[-1]

                    self.launch(latest_local)

            else:
                if self.downloadable_versions:
                    print("Downloading latest version (CLEAN START)")
                    # DOWNLOAD
                    latest_online = list(sorted(
                        self.downloadable_versions.keys()))[-1]
                    self.download_version(latest_online)
                    self.launch(latest_online)
                    # download latest online
                else:
                    # DONTLAUNCH
                    print("Unable to launch version", self.use_version,
                          "without internet connection")

        else:
            if self.downloaded_versions:
                if self.downloadable_versions:
                    if self.use_version in self.downloaded_versions: 
                        print("Using local version, internet is available")
                        # use rather downloaded (preference) # LOCAL
                        self.launch(self.use_version)
                    else:
                        # DOWNLOAD
                        print("Downloading specified version...")
                        self.download_version(self.use_version)
                        self.launch(self.use_version)
                else:
                    if self.use_version in self.downloaded_versions:
                        print("Using local version, internet is unavailable")
                        self.launch(self.use_version)
                        # use local # LOCAL
                    else:
                        # DONTLAUNCH
                        print("Sorry, you need an internet connection :o")
            else:
                if self.downloadable_versions:
                    print("Downloading version", self.use_version)
                    self.download_version(self.use_version)
                    self.launch(self.use_version)
                    # download nth online # DOWNLOAD
                else:
                    # DONTLAUNCH
                    print("Unable to launch", self.use_version,
                          "without internet connection")

        self.update_state()

        # N-th launch, using version that is online - internet is required

        # N-th launch, using version that is local - no internet required


if __name__ == "__main__":
    with open("client.json") as f:
        client_config = json.load(f)

    version_provider, downloaded_versions, use_version = client_config.values()

    main = Main(version_provider, downloaded_versions, use_version)

    main.main()
