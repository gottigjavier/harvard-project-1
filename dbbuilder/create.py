from mymodels import *
from myconfig import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app) # Here it is linked db with app

def main():
    db.create_all()
    print("Tables have been created successfully.")

if __name__ == "__main__":
    with app.app_context():
        main()
