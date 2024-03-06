## What is TorGhost ?
TorGhost is an anonymization script. TorGhost redirects all internet traffic through SOCKS5 tor proxy. DNS requests are also redirected via tor, thus preventing DNSLeak. The scripts also disables unsafe packets exiting the system. Some packets like ping request can compromise your identity.

## How to install ?
**New kali update is causing permission error, please build and install from source**

TorGhost can be installed by downloading the [latest release](https://github.com/SusmithKrishnan/torghost/releases) using debian package manager

Download

` wget -c https://github.com/SusmithKrishnan/torghost/releases/download/v3.0.2/torghost-3.0.2-amd64.deb`


`sudo dpkg -i torghost-*-amd64.deb`

## Build and install from source (reccomended)
`git clone "https://github.com/quintin2003/torghost"`

`cd torghost`

`chmod +x build.sh`

`./build.sh`r

## Usage
Torghost v3.0 usage:

  `-s      --start      Start Torghost`

  `-r      --switch      Request new tor exit node`

`  -x      --stop      Stop Torghost`

`  -h      --help      Print this help and exit`





