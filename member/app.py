from flask import Blueprint  # 載入 Blueprint 物件
from flask import render_template   # 載入 render_template 物件
from flask import request   # 載入 request 物件

member = Blueprint('member', __name__, template_folder='member_templates')


@member.route("/")
def index():
    return render_template("member.html")

@member.route("/profile")
def profile() :
    name = 'Darren'
    email = 'darren@test.com'
    return render_template("member_profile.html", name=name, email=email)