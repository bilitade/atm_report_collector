# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['gui.py'],  # Update with your main script file
             pathex=['.'],
             binaries=[],
             datas=[('assets/logo.png', 'assets'), ('assets/coop.ico', 'assets')],  # Include your icon and image files here
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='GUI',  # Update the name of your executable if needed
          debug=False,
          strip=False,
          upx=True,
          console=True)
