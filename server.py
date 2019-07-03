from sanic import Sanic
from sanic.log import logger
from api.routes import api_bp

app = Sanic()
app.config.REQUEST_MAX_SIZE = 1000000 # max request size 1MB

app.blueprint(api_bp)

if __name__ == '__main__':
    settings = {
        'host': '127.0.0.1',
        'port': 8080,
        'debug': False, 
        'access_log': True
    }
    app.run(**settings)
