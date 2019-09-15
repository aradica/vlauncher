import io
import json
import os
import time
import zipfile

import requests


class Main:
    def __init__(self, configuration):
        self.version_provider = configuration.get("version_provider")

        self.update_check_pause = int(configuration.get("update_check_pause"))
        self.last_update_check = int(configuration.get("last_update_check"))
        self.use_version = configuration.get("use_version")

        self.downloaded_versions = configuration.get("downloaded_versions")
        self.downloadable_versions = {}

        self.able_to_launch = True

    def get_downloadable_versions(self):
        now = time.time()
        time_since_check = now - self.last_update_check
        print("Time since last check:", time_since_check)
        if time_since_check > self.update_check_pause:
            print("Wait period has expired!")
            if "https" not in self.version_provider[:5]:
                print("Using local version provider")
                with open(self.version_provider) as f:
                    server = json.load(f)

                self.downloadable_versions = server.get("versions")

                # Could possibly change on server side
                self.update_check_pause = server.get("update_check_pause")

                # And remember it
                self.last_update_check = now
            else:
                print("Attempting to use online version provider")
                try:
                    response = requests.get(self.version_provider)
                    print("Server response:", response)
                    server = response.json()
                    self.downloadable_versions = server.get(
                        "versions")
                    # Could possibly change on server side
                    self.update_check_pause = server.get("update_check_pause")
                    self.last_update_check = now
                except Exception as e:
                    print("Failed to use online version provider:", e, sep="\n")
                    self.downloadable_versions = None

        else:
            print("Current configuration limits this update check frequency")
            self.downloadable_versions = None

    def download_version(self, version):
        print(version)
        link = self.downloadable_versions.get(version).get("download")
        print(link)
        if "https" not in link[:5]:
            print("Attempting to download from local server...")
            try:
                with zipfile.ZipFile(link, "r") as zip:
                    print("Extracting...")
                    zip.extractall()  # path?
            except Exception:
                print("Failed to download local version!")
                self.able_to_launch = False

        else:
            print("Attempting to downloading from internet")
            try:
                response = requests.get(link)
                in_memory = io.BytesIO(response.content)
                archive = zipfile.ZipFile(in_memory, "r")
                print("Extracting...")
                archive.extractall()
            except Exception:
                print("Failed to download from internet!")
                self.able_to_launch = False

        # update changes to self
        app_main = self.downloadable_versions.get(version).get("main")
        self.downloaded_versions.update({version: {"main": app_main}})

    def launch(self, version):
        self.update_state()
        if self.able_to_launch:
            run = self.downloaded_versions.get(version)
            print("Launching", version, "with", run.get("main"))
            os.chdir(version)
            print("---RUNNING---")
            os.system(run.get("main"))
        else:
            print("Unable to launch!")

    def update_state(self):
        config = {
            "version_provider": self.version_provider,
            "update_check_pause": self.update_check_pause,
            "last_update_check": self.last_update_check,
            "downloaded_versions": self.downloaded_versions,
            "use_version": self.use_version
        }
        with open("client.json", "w") as f:
            f.write(json.dumps(config, indent=4))

    def validate_configuration(self):
        # Actual versions
        versions = [v for v in os.listdir() if v in self.downloaded_versions]

        # If what-i-think-i-have minus what-i-actually-have == {},
        # then it's all good
        difference = set(self.downloaded_versions) - set(versions)
        if difference:
            print("Some versions are no longer present:", difference)
            for d in difference:
                self.downloaded_versions.pop(d)
        else:
            print("Files present")

    def main(self):
        print("Launcher started!")
        self.validate_configuration()
        self.get_downloadable_versions()
        # print(self.downloadable_versions)
        if self.use_version == "latest":
            print("Latest version check:")
            if self.downloaded_versions:
                if self.downloadable_versions:
                    # compare versions, download only if not actual latest
                    latest_local = list(
                        sorted(self.downloaded_versions.keys()))[-1]
                    latest_online = list(sorted(
                        self.downloadable_versions.keys()))[-1]
                    print("Latest local", latest_local)
                    print("Latest online", latest_online)
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
                    # Check update frequency again (reason for not checking)
                    now = time.time()
                    time_since_check = now - self.last_update_check
                    if time_since_check > self.update_check_pause:
                        print("Didn't check for latest (couldn't)")
                        # LOCAL
                    else:
                        print("Didn't check for latest (configuration)")
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
                        self.update_state()
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

    main = Main(client_config)

    main.main()
