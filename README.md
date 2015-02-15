MountAndLaunch
==============

Small Python program that mounts Samba points to local folders. If all these mounts are succesful it will then launch applications.

Currently 'settings.cfg' is hardcoded and expects the following structure:
    [mount-points]
    ;** mount point structure: destination-server/path,local/path,username,password
    ;** examples:
    ; point1 = samba-server/path1,/volumes/path1,username,password
    ; point2 = samba-server/path2,/volumes/path2,username,password

    [launch-apps]
    ;** launch app examples:
    ; app1 = open -n /applications/itunes.app
    ; app2 = open -n /applications/textedit.app


Only tested on OSX Yosemite at the moment.