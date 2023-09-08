# 初始化 Flask 伺服器
from flask import Flask
from flask import redirect
from home.app import home
from create_account.app import create_account
from member.app import member
from bill_information.app import bill_information
from database import account_database

app = Flask(
    __name__,
    static_folder="public",
    static_url_path="/"
)
app.secret_key = "P@ssw0rd1234"

app.config['account_database'] = account_database()

@app.route("/")
def go_home_page() :
    return redirect("/home")

app.register_blueprint(home, url_prefix='/home')   # 透過 bluesprint 管理 home page

app.register_blueprint(create_account, url_prefix='/create_account')

app.register_blueprint(member, url_prefix='/member')

app.register_blueprint(bill_information, url_prefix='/bill_information')

app.run(port=3000, debug=True)