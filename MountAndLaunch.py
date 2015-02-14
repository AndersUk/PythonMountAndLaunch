#!/usr/bin/python

import subprocess
import os
import ConfigParser

def log( obj ):
    print( obj )

def createConfiguration( fname ):
    if( os.path.isfile(fname) ):
        log( 'Configuration file \'{}\' already exists'.format( fname ) )
        return False
    else:
        config = ConfigParser.RawConfigParser(allow_no_value = True)

        config.add_section('mount-points')
        config.set('mount-points', ';** Mount Point structure: destination-server/path,local/path,username,password')
        config.set('mount-points', ';** Examples:')
        config.set('mount-points', '; point1 = samba-server/path1,/Volumes/Path1,username,password')
        config.set('mount-points', '; point2 = samba-server/path2,/Volumes/Path2,username,password')
        
        config.add_section('launch-apps')
        config.set('launch-apps', ';** Launch App examples:')
        config.set('launch-apps', '; app1 = open -n /Applications/iTunes.app')
        config.set('launch-apps', '; app2 = open -n /Applications/TextEdit.app')
        
        # Writing our configuration file to 'example.cfg'
        with open(fname, 'wb') as configfile:
            config.write(configfile)
        
        return True
        
def loadConfiguration( fname ):
    if( not os.path.isfile(fname) ):
        log( 'Configuration file \'{}\' doesn\'t exist'.format( fname ) )
        return None
      
    config = ConfigParser.RawConfigParser(allow_no_value = True)
    config.read(fname)
    
    cmpoints = config.items('mount-points')
    clapps = config.items('launch-apps')
    
    mpoints = []
    for key, value in cmpoints:
        r = convertMountSettingLineToObject( value )
        if( not r is None ):
            mpoints.append( r )
            
    apps = []
    for key, value in clapps:
        apps.append(value)
    
    _return = { 'mount-points': mpoints, 'launch-apps': apps}
    return _return
        
def convertMountSettingLineToObject( item ):
    elements = item.split( ',' )
    if( len( elements ) != 4 ):
        log( 'Invalid mount line: \'{}\''.format(item))
        return None
        
    _return = {'destination':elements[0], 'local':elements[1], 'username':elements[2], 'password':elements[3] }
    return _return
    
def makeLocalFolders(wantedMountPoints):
    #** Check local path exists
    for mp in wantedMountPoints:
        if not os.path.exists(mp['local']):
            os.makedirs(mp['local'])
    
def mountMain( wantedMountPoints ):
    wmps = wantedMountPoints[:]
    
    #** Create local folders
    makeLocalFolders( wmps )
    
    #** Get existing mount points
    existingMounts = getExistingMounts()
        
    #** Unmount unwanted local points
    unmountExistingMounts(wmps, existingMounts)
    
    #** Create local folders, incase unmout removed them
    makeLocalFolders( wmps )
    
    #** Mount wanted mounts
    mountWantedMounts( wmps )
    
    #** Refresh existing mount points
    existingMounts = getExistingMounts()
    
    #** Unmount unwanted local points
    unmountExistingMounts(wmps, existingMounts)
    if( len(wmps) > 0):
        log('Not all mounts successful:')
        log(wmps)
        return False
    else:
        log('All mounts successful - launching applications')
        return True
    
  
def getExistingMounts():
    #** 1) --------------------------------------
    #** Get the list of known mounts
    p = subprocess.Popen(['mount'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    lines = out.splitlines(False)

    #** Lift out lines which are samba mounts
    existingMounts = []
    for l in lines:
        if( 'smbfs' in l ):
            existingMounts.append(l)
        
    parsedExistintMounts = []
    for l in existingMounts:
        parsedExistintMounts.append( parseMountLine(l) )
    
    return parsedExistintMounts
                      
def parseMountLine( mountline ):
    #** Multiple steps to strip out unwanted bits such as: (smbfs, nodev, nosuid)
    step1 = mountline.rsplit( ' (' )[0:1]
    step2 = step1[0].split( ' on ')
    step3 = step2[0].split( '@')[1:]
    
    return { 'destination': step3[0], 'local':step2[1] }
    
def unmountExistingMounts(wantedMountPoints, existintMounts):
    #** Unmount any mount points that match local, but don't match destination
    alreadyMounted = []
    for pmp in existintMounts:
        for mp in wantedMountPoints:
            if( ( mp['local'] == pmp['local'] ) and ( mp['destination'] != pmp['destination']) ):
                log( 'Unmounting: \'{}\' as mounted to: \'{}\''.format( pmp['local'],  pmp['destination']))
                um = subprocess.Popen(['umount', '-f', mp['local']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = um.communicate()
                
            #** Make a note of any mounts that match a Wanted Mount Point
            if( ( mp['local'] == pmp['local'] ) and ( mp['destination'] == pmp['destination']) ):
                alreadyMounted.append(mp)
                
    #** Remove any good mount points from the Wanted Mount Points as
    #** they're already there and good            
    if( len(alreadyMounted) > 0):
        for a in alreadyMounted:
            wantedMountPoints.remove(a)

def mountWantedMounts( wantedMountPoints ):
    for mp in wantedMountPoints:
        #** Check for username/password
        auth = ''
        if( mp['username'] and mp['password'] ):
            auth = '{}:{}@'.format( mp['username'], mp['password'] )
            
        if( mp['username'] and not mp['password'] ):
            auth = '{}@'.format( mp['username'] )
          
        #** Built mount string  
        dest = '//{}{}'.format(auth, mp['destination'] )
        
        #** Execute command
        try:
            log( 'Mounting: \'{}\' to: \'{}\''.format( mp['destination'], mp['local']))
            um = subprocess.Popen(['/sbin/mount','-t', 'smbfs', dest, mp['local']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = um.communicate()
        except:
            pass

def lauchMain( launchApps ):
    for la in launchApps:
        lae = la.split(' ')
        log( 'Launching: \'{}\''.format(la))
        um = subprocess.Popen(lae, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = um.communicate()        


if __name__ == '__main__':
    fname = 'settings.cfg'

    config = loadConfiguration(fname)
    if( config is not None ):
        if( mountMain(config['mount-points']) ):
            lauchMain(config['launch-apps'])
    
    