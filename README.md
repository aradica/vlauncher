# vlauncher
Version manager &amp; launcher for critical systems.
Part of a bigger project I have in mind that will enable anyone to use simple cloud hosting services as a platform to deliver software updates.

## How to use with Google Disk:
Create a folder on Google Disk that will host your software releases. In the root of the folder, create a `server.json` file (you can view the example at the end for more clarification). This file will be checked by `vlauncher` whenever it is launched and there is an internet connection. The `server.json` looks something like this:
```
{
    "versions": {
        "1.0.0": {
            "download": "https://drive.google.com/uc?export=download&id=<some_numbers>",
            "main": "main.py"
        },
        "1.0.1": {
            "download": ""https://drive.google.com/uc?export=download&id=<some_numbers>",
            "main": "main.py"
        }
    }
}
```
The download links lead to zipped updates that will get unpacked by `vlauncher`.
You can obtain a direct download link from Google Disk and use it to provide updates for software you release using `vlauncher` (by placing it under "download" for each version"). To do so, just create a shareable link (that people can only view!) and change `open?` with `uc?export=download&`.

`vlauncher` also enables you to choose which version do you want to launch. There should also be a `client.json` file in the root folder of every software user. An example would be:
```
{
    "version_provider": "https://drive.google.com/uc?export=download&id=<some_numbers>",
    "downloaded_versions": {
        "1.0.0": {
            "main": "main.py"
        }
    },
    "use_version": "latest"
}
```
Visualized example folder structure for cloud:
```
your_project
│   server.json    
│   1.0.0.zip
│   1.0.1.zip
```
And locally:
```
your_project
│   client.json
│   vlauncher.py
└───1.0.0.
│   │   main.py
│
└───1.0.1.
│   │   main.py
```
Currently, this is still in the development stage (and it misses some security features!), but it should soon be ready for basic usage :)
