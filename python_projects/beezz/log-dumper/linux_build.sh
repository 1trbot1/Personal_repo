python3.8 -m PyInstaller --log-level CRITICAL --clean --distpath ./exec/linux --specpath /tmp/pytinstaller --workpath /tmp/pytinstaller --onefile --console -n ld "./main.py"
cp -r ./config  ./exec/linux