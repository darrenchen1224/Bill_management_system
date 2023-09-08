from flask import Blueprint, current_app  # 載入 Blueprint 物件
from flask import render_template   # 載入 render_template 物件
from flask import request   # 載入 request 物件



create_account = Blueprint('create_account', __name__, template_folder='create_account_templates')


@create_account.route("/")
def index():
    return render_template("create_account.html")

@create_account.route("/create", methods=['POST'])
def create():
    account = request.form["account"]
    password = request.form["password"]
    name = request.form["name"]
    email = request.form["email"]
    db = current_app.config['account_database']
    collection = db.users

    # 比對資料庫是否有相同的帳號
    data = collection.find_one(
        {
            "account" : account
        }
    )

    # 確認使用者皆有填寫
    if (account == '') or (password == '') or (name == '') or (email == '') :
        return "Your informations are incomplete!"
    
    # 確認使用者的帳號沒註冊過
    elif data :
        return "This account already registered!"
    
    else :
        # 將使用者資訊新增至資料庫
        collection.insert_one(
            {
                "account" : account,
                "password" : password,
                "name"  : name,
                "email" : email
            }
        )
        print("新增一筆資料成功")
        return render_template("success.html")