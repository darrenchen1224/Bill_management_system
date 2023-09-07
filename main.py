# 連線到 MongoDB 雲端資料庫
from pymongo.mongo_client import MongoClient
import urllib.parse  # 因密碼有 @ ，因此載入 urlib.parse 套件，解析 URL

username = urllib.parse.quote_plus('Darren')
password = urllib.parse.quote_plus('P@ssw0rd1234')
client = MongoClient(
    "mongodb+srv://%s:%s@mycluster.a0nsuov.mongodb.net/?retryWrites=true&w=majority" % (username, password))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# 建立資料庫
db = client.member_system


# 初始化 Flask 伺服器
from flask import Flask
from flask import redirect
from home.app import home
from create_account.app import create_account
from member.app import member

app = Flask(
    __name__,
    static_folder="public",
    static_url_path="/"
)
app.secret_key = "P@ssw0rd1234"

@app.route("/")
def go_home_page() :
    return redirect("/home")

app.register_blueprint(home, url_prefix='/home')   # 透過 bluesprint 管理 home page

app.register_blueprint(create_account, url_prefix='/create_account')

app.register_blueprint(member, url_prefix='/member')

app.run(port=3000)