set -eu
cd /home/ros/Downloads/garage-app-install
python3 - <<'PY'
import hashlib,pathlib
p=pathlib.Path('FreeCAD_1.1.3.AppImage')
expected=pathlib.Path('FreeCAD.sha256').read_text().split()[0]
actual=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert actual==expected,(actual,expected)
print('FreeCAD checksum verified:',actual)
PY
chmod +x FreeCAD_1.1.3.AppImage
./FreeCAD_1.1.3.AppImage --appimage-extract > freecad-extraction.log
sudo -n mkdir -p /opt/freecad-1.1.3
sudo -n cp -a squashfs-root/. /opt/freecad-1.1.3/
sudo -n ln -sfn /opt/freecad-1.1.3/AppRun /usr/local/bin/freecad
cat > freecad.desktop <<'DESKTOP'
[Desktop Entry]
Type=Application
Name=FreeCAD
Comment=Parametric 3D CAD modeler
Exec=/usr/local/bin/freecad %F
Icon=/opt/freecad-1.1.3/org.freecad.FreeCAD.svg
Terminal=false
Categories=Graphics;Engineering;
MimeType=application/x-extension-fcstd;
DESKTOP
sudo -n mkdir -p /usr/local/share/applications
sudo -n install -m 644 freecad.desktop /usr/local/share/applications/freecad.desktop
desktop-file-validate /usr/local/share/applications/freecad.desktop
ls /opt/freecad-1.1.3
sudo -n chown -R root:root /opt/freecad-1.1.3
/opt/freecad-1.1.3/AppRun freecadcmd --version
