from flask import Blueprint, current_app, session  # 載入 Blueprint 物件
from flask import render_template   # 載入 render_template 物件
from flask import request   # 載入 request 物件
from flask import redirect


home = Blueprint('home', __name__, template_folder='home_templates')


@home.route("/")
def index():
    return render_template("home.html")

@home.route("/authentication", methods=["POST"])
def compare() :
    account = request.form["account"]
    password = request.form["password"]
    db = current_app.config['account_database']
    collection = db.users
    data = collection.find_one(
        {
            "$and" :[
                {
                    "account" : account
                },
                {
                    "password" : password
                }
            ]
        }
    )
    


    # 若沒有填寫帳號或密碼
    if (account == '') or (password == '') :
        return "Your account or password are incomplete"

    # 從資料庫中比對到正確的帳號密碼
    elif data :
        # 將登入的使用者資料存到 session
        session['account'] = data['account']
        session['password'] = data['password']
        session['name'] = data["name"]
        session["email"] = data["email"]
        return redirect('/member')
    
    # 資料庫中比對不到該帳號或密碼
    else :
        return "Wrong account or password !"