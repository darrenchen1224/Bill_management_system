from flask import Blueprint  # 載入 Blueprint 物件
from flask import render_template   # 載入 render_template 物件
from flask import request   # 載入 request 物件
from flask import redirect

home = Blueprint('home', __name__, template_folder='home_templates')


@home.route("/")
def index():
    return render_template("home.html")

@home.route("/authentication")
def compare() :
    if True :
        return redirect("/member/profile")