import os
import tqsdk
import argparse
import PyInstaller.__main__

# > python3 tqinstaller.py --_file xxxxx.py

parser = argparse.ArgumentParser()
parser.add_argument("--_file", type=str, required=True)
args, unknown = parser.parse_known_args()
file_path = os.path.realpath(args._file)
package_name = os.path.splitext(os.path.basename(file_path))[0]
dirname = os.path.dirname(tqsdk.__file__)

PyInstaller.__main__.run([
    '--noconfirm',
    '--D'
    '--name=%s' % package_name,
#    '--onefile',
    '--add-data=%s;%s' % (os.path.join(dirname, 'web', '*.*'), os.path.join('tqsdk', 'web')),
    '--add-data=%s;%s' % (os.path.join(dirname, 'web', 'js', '*.*'), os.path.join('tqsdk', 'web', 'js')),
    '--add-data=%s;%s' % (os.path.join(dirname, 'web', 'css', '*.*'), os.path.join('tqsdk', 'web', 'css')),
    '--add-data=%s;%s' % (os.path.join(dirname, 'web', 'fonts', '*.*'), os.path.join('tqsdk', 'web', 'fonts')),
    '--add-data=%s;%s' % (os.path.join(dirname, 'web', 'img', '*.*'), os.path.join('tqsdk', 'web', 'img')),
    '--add-data=%s;%s' % (os.path.join(dirname, 'web', 'img', 'icons', '*.*'), os.path.join('tqsdk', 'web', 'img', 'icons')),
    '--icon=%s' % os.path.join(dirname, 'web', 'favicon.ico'),
    file_path,
])
