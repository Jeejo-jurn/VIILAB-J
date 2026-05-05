@echo off
echo Creating Virtual Environment...
python -m venv .venv

echo Activating Virtual Environment...
call .venv\Scripts\activate

echo Upgrading PIP...
python -m pip install --upgrade pip

echo Uninstalling conflicting libraries...
pip uninstall -y opencv-python opencv-contrib-python dlib face_recognition cmake

echo Installing Dependencies...
pip install -r requirements.txt

echo Done!
pause
