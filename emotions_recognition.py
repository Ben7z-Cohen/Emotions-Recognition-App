from app_engine import AppEngine
from application import Application


if __name__ == '__main__':
    engine = AppEngine()
    app = Application(engine)
    app.run()




