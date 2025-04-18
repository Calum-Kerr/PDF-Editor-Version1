from flask import Flask
import os

app = Flask(__name__, template_folder='../templates')

# Add custom filter
@app.template_filter('basename')
def basename_filter(path):
    return os.path.basename(path)

from app import routes
from tools.optimise import compress
