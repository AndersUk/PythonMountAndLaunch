MountAndLaunch
==============

Small Python program that mounts Samba points to local folders. If all these mounts are successful it will then launch local applications (which most likey make use of said mount points). 

This program simply loads a configuration file that contains a list of Samba shares to be mounted/mapped. If all of these mounts are successful it'll move onto a list of applications to be launched. 

**Usage**: 

1) Run it once to generate an example configuration file (default filename: `settings.cfg`): 

    ./MountAndLaunch.py -g

2) Edit `settings.cfg` with your favourite text editor. 

2.1) Type your specific samba server details and also I'd recommend setting the local path to begin with:

    /Volumes

2.2) For example, type the following launch command to start iPhoto with the desired library:

    app1 = open -F "/Volumes/Photo/<path to library>/<library name>.photolibrary"

3) Run the Python program again and see what happens

    ./MountAndLaunch.py


**Example Config File**:

Currently `settings.cfg` expects the following structure:

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