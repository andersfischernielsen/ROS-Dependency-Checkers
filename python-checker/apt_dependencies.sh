apt-get update
apt-get install -y curl
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
rm get-pip.py
pip install flake8 flake8-requirements