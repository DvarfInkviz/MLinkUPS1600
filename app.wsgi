import sys
sys.path.insert(0, '/var/www/web-ups1600')

activate_this = '/home/microlink/.local/share/virtualenvs/web-ups1600-AkuQ4JLQ/bin/activate_this.py'
with open(activate_this) as file_:
	exec(file_.read(), dict(__file__=activate_this))

from app import app as application
