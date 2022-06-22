# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['app.py'],
             pathex=['C:\\Users\\Ilay\\Desktop\\php\\Cheque_Print_Python'],
             binaries=[],
             datas=[('app.db', '.'),
					('C:\\Users\\Ilay\\Desktop\\php\\Cheque_Print_Python\\image\\blank.png', 'image'),
                    ('C:\\Users\\Ilay\\Desktop\\php\\Cheque_Print_Python\\image\\Template.png', 'image'),
                    ('C:\\Users\\Ilay\\Desktop\\php\\Cheque_Print_Python\\temp\\PARTY_NAME.csv', 'temp'),
                    ('C:\\Users\\Ilay\\Desktop\\php\\Cheque_Print_Python\\temp\\DEPARTMENT.csv', 'temp'),
                    ('C:\\Users\\Ilay\\Desktop\\php\\Cheque_Print_Python\\print\\sample.pdf', 'print')],
             hiddenimports=['babel.numbers'],
             hookspath=[],
             hooksconfig={},
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
          [],
          name='cheque_printer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )