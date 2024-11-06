from flask import Flask
from app import routes
app = Flask(__name__, template_folder='../templates')