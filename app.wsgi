import sys
sys.path.insert(0, '/var/www/web-gost-crypt-2')

activate_this = '/home/threeline/.local/share/virtualenvs/web-gost-crypt-2-bmdxSJl1/bin/activate_this.py'
with open(activate_this) as file_:
	exec(file_.read(), dict(__file__=activate_this))

from app import app as application
