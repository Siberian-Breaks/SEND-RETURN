# SEND-RETURN

![SEND/RETURN](https://raw.githubusercontent.com/Siberian-Breaks/SEND-RETURN/main/projectbanner.png "SEND/RETURN")

SEND/RETURN is an entirely new way to experience music! It solves your song-searching issues, from the comfort of a uniquely generated virtual environment. This enables multiple users to discover similar-sounding songs together.

[Quick start guide](https://github.com/Siberian-Breaks/SEND-RETURN/blob/main/quick-start-guide.pdf)

## Hosting a local (LAN) server:
1. Clone our repo and `cd ./flask-server/`
2. Create a virtual environment with `python3 -m venv [venv-name]`
3. Install requirements with: `pip3 install -r requirements.txt`
4. Execute: `flask run -p 5000 -h 0.0.0.0`
5. Install the [development build of SEND/RETURN from our releases page](https://github.com/Siberian-Breaks/SEND-RETURN/releases/tag/dev-build-0.99 "Development build")
6. When executed, click on 'host' at the main menu.
7. All users on your LAN will be able to discover you lobby with the 'join' button.

## Hosting a public (internet) server:
1. Install the development build of SEND/RETURN from our releases page
2. Click 'host' at the main menu.
3. Hit 'Tab' and select 'global server' at the bottom left of the UI
4. Share your external IP with friends
5. Have your friends hit `~` at the main menu, and type: `open [IP]`.

(Global server is hosted on our dedicated server, and we cannot guarantee it will always be up.)

## Joining a server:
1. Install the development build of SEND/RETURN from our releases page

2. If joining a LAN server >>
  Click 'join' at main menu and the listen-server sessions will appear

3. If joining a public server >>
  Press `~` and type `open [IP]` to connect.
  
--------------------------------------------------------------------------------------------------------------------------------------------------------------



![Flask values](https://raw.githubusercontent.com/Siberian-Breaks/SEND-RETURN/main/values.png "Flask values")
