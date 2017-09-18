import os

from app import create_app
#impor configurations for running the app
config_name = os.getenv('APP_SETTINGS')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(port=5000)
