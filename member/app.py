from flask import Blueprint, session, current_app, redirect  # 載入 Blueprint 物件
from flask import render_template   # 載入 render_template 物件
from flask import request   # 載入 request 物件

member = Blueprint('member', __name__, template_folder='member_templates')


@member.route("/")
def profile() :
    name = session['name']
    email = session["email"]
    return render_template("member_profile.html", name=name, email=email)

@member.route("/modify_profile")
def modify() :
    return render_template("modify_profile.html")

@member.route("/validate", methods=["POST"])
def validate() :
    old_account = session['account']
    name = request.form["name"]
    email = request.form["email"]

    if (name == '') or (email == '' ) :
        return "Your informations are incomplete!"
    else :
        db = current_app.config['account_database']
        collection = db.users
        collection.update_one(
            {
                "account" : old_account
            },
            {
                "$set" : {
                        "name" : name,
                        "email" : email
                }
            }
        )
        session['name'] = name
        session['email'] = email

        return redirect("/member")