echo "Creating python environment"
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
pip install --upgrade pip