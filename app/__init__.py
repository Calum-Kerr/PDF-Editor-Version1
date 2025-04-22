from flask import Flask
app = Flask(__name__, template_folder='../templates')
app.secret_key = 'dev'  # Simple development key, change in production

from app import routes
from tools.optimise import compress