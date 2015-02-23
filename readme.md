intro
=====
these utils is used for downloaded MMD model.

features
========
1. view pmx/pmd model
2. solved the shift_jis display a unknown string in ms-windows(maybe chinese windows only).

requirement
===========
1. python 2.7.x
2. pyqt 4.8.x
3. latest fbx-python from autodesk inc.
4. chardet
5. latest PIL/Pillow
6. panda3d 1.8.x+
7. pymeshio
8. wxPython 3.0.2


usage
=====
1. sjis2utf8.exe/sjis2utf8.py
  rename the folder/file name encoded by shift_jis to human-reading in ms-windows,
  it auto rename all entry in specified folder with recursion
2. shiftjis2utf8_text.pyw
  drag-drop text files from windows explorer to app gui, it maybe auto converting
  known encoded files to utf-8, supported overwrite or not(default).
3. fbxhana4c4d.py
  convert node name with shift-jis in fbx file to unicode '\uxxxx' mode for cinema4d read it.
  it supported ascii/binary because using official fbx-python package read/write.
4. ViewPMD.py
  using panda3d display PMX model. it using pymeshio package read MMD model

bugs
====
1. if file/folder name has some katakana char, maybe can not rename it.
  etc: middle dot (U+30FB, \u30FB),
2. some mmd model maybe texture error

license
=======
1. DrawPlane.py get from Panda3D community:
  Three Axis Coordinate Plane Grid Class (ThreeAxisGrid)
  Mathew Lloyd AKA 'Forklift', August 2008, 'matthewadamlloyd@gmail.com'
  note: I changed some code for my code usage.
2. all other used package is follow original.
3. My owner code is follow MIT License.

