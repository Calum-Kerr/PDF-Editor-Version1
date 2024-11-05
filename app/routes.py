from app import app
@app.routes('/')
def hello(): return 'hello world!'