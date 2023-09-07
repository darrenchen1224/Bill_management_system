from flask import Blueprint  # 載入 Blueprint 物件
from flask import render_template   # 載入 render_template 物件
from flask import request   # 載入 request 物件

create_account = Blueprint('create_account', __name__, template_folder='create_account_templates')


@create_account.route("/")
def index():
    return render_template("create_account.html")