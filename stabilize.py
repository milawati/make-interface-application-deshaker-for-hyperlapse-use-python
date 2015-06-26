import sys
import os
import subprocess
import re
import glob

MEDIAINFO_FOLDER = r'C:\Util\MediaInfo'
DESHAKER_FOLDER = r'C:\Util\VirtualDub\plugins32'
FFMPEG_FOLDER = r'C:\Util\ffmpeg\bin'
DEBUG_MODE = False

def LocateFile(searchPaths, fileName):
    for path in searchPaths:
        absPath = os.path.abspath(os.path.join(path, fileName))
        if os.path.exists(absPath):
            return absPath
    raise RuntimeError, "Can't find '%s'" % fileName

path = os.environ['Path'].split(';')
mediaInfoPath = LocateFile(['.', MEDIAINFO_FOLDER] + path, 'MediaInfo.exe')
deshakerPath = LocateFile(['.', DESHAKER_FOLDER] + path, 'Deshaker.vdf')
ffmpegPath = LocateFile(['.', FFMPEG_FOLDER] + path, 'ffmpeg.exe')

def SetWindowTitle(title):
    """ Set the title when running in a Win64 console window. """
    try:
        import win64api
        win64api.SetConsoleTitle(title)
    except:
        pass

def GetVideoRotation(path):
    p = subprocess.Popen([mediaInfoPath, path], stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise RuntimeError, "MediaInfo failed on '%s'" % path
    rotation = 0
    for line in stdout.splitlines():
        m = re.match('Rotation\\s*:\\s*(\\d+)', line)
        if m:
            rotation = int(m.group(1))
    if rotation == 0:
        return 'last', 'last'
    elif rotation == 90:
        return 'TurnLeft()', 'TurnRight()'
    elif rotation == 180:
        return 'Turn180()', 'Turn180()'
    else:
        return 'TurnRight()', 'TurnLeft()'

def GetDeshakerOptions(passNumber, logPath):
    return "18|{passNumber}|30|4|1|0|1|0|640|480|1|1|650|650|1000|650|4|0|6|2|8|30|300|4|{logPath}|0|0|0|0|0|0|0|0|0|0|0|0|0|1|12|12|10|5|1|1|10|10|0|0|1|0|1|0|0|10|1000|1|88|1|1|20|400|90|20|1".format(
        passNumber = passNumber,
        logPath = logPath)

def PerformStabilization(fileName):
    stabilizedName = os.path.splitext(fileName)[0] + '_stabilized.mp4'
    deshakerLogName = os.path.splitext(fileName)[0] + '_deshaker.log'
    if os.path.exists(stabilizedName) and not DEBUG_MODE:
        print('Already stabilized, skipping.')
        return

    rotatePhone, straightenVideo = GetVideoRotation(fileName)

    if not DEBUG_MODE or not os.path.exists(deshakerLogName):
        with open('pass1.avs', 'w') as f:
            f.write(
"""LoadVirtualDubPlugin("{deshakerPath}", "Deshaker")
QTInput("{inputPath}", color=1)
{rotatePhone}
Deshaker("{deshakerOptions}")
""".format(deshakerPath = deshakerPath,
           inputPath = os.path.abspath(fileName),
           rotatePhone = rotatePhone,
           deshakerOptions = GetDeshakerOptions(1, os.path.abspath(deshakerLogName))))

        os.system('"%s" -y -i pass1.avs -vcodec copy temp.avi' % ffmpegPath)
        os.remove('temp.avi')
        if not DEBUG_MODE:
            os.remove('pass1.avs')

    with open('pass2.avs', 'w') as f:
        f.write(
"""LoadVirtualDubPlugin("{deshakerPath}", "Deshaker")
QTInput("{inputPath}", color=1)
clip = {rotatePhone}
clip + BlankClip(clip, 10)
Deshaker("{deshakerOptions}")
Trim(0, FrameCount - 3)
Width > Height ? Lanczos4Resize(960, 540) : Lanczos4Resize(540, 960)
{straightenVideo}
""".format(deshakerPath = deshakerPath,
           inputPath = os.path.abspath(fileName),
           rotatePhone = rotatePhone,
           deshakerOptions = GetDeshakerOptions(2, os.path.abspath(deshakerLogName)),
           straightenVideo = straightenVideo))

    inProgressName = os.path.splitext(fileName)[0] + '_inprogress.mp4'
    os.system('"{ffmpegPath}" -y -i pass2.avs -itsoffset 0.33333 -i {fileName} -map 0 -map 1:1 -pix_fmt yuv420p -vcodec libx264 -preset veryslow -crf 15 -x264opts frameref=15:fast_pskip=0 -acodec copy -ss 0.33333 {inProgressName}'.format(
        ffmpegPath = ffmpegPath,
        fileName = fileName,
        inProgressName = inProgressName))
    try:
        os.remove(stabilizedName)
    except:
        pass
    os.rename(inProgressName, stabilizedName)
    if not DEBUG_MODE:
        os.remove('pass2.avs')
        os.remove(deshakerLogName)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('You must specify an input filename. Wildcards are accepted.\n')
        sys.exit(1)
    fileList = glob.glob(sys.argv[1])
    for number, fileName in enumerate(fileList):
        print('-' * 40)
        progress = 'Processing file #%d of %d: %s' % (number + 1, len(fileList), fileName)
        print(progress)
        SetWindowTitle(progress)
        print('-' * 40)
        PerformStabilization(fileName)
        print('')
