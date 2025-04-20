from flask import Flask
app = Flask(__name__, template_folder='../templates')

# Move forms directory into app package first, then use:
from app.forms.security import ProtectPDFForm
from app import routes
from tools.optimise import compress