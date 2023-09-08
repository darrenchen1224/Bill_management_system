from flask import Blueprint, redirect, session, current_app  # 載入 Blueprint 物件
from flask import render_template   # 載入 render_template 物件
from flask import request   # 載入 request 物件


bill_information = Blueprint('bill_information', __name__, template_folder='bill_templates')


@bill_information.route("/")
def index():
    return render_template("bill_info.html")


@bill_information.route("/parking_fee")
def parking():
    db = current_app.config['account_database']
    collection = db.users
    account = session["account"]
    data = collection.find_one(
        {
            "account" : account
        }
    )
    vehicle = data['vehicle']
    first_num = data['first_num']
    last_num = data['last_num']
    return render_template("parking_fee.html", vehicle=vehicle, first_num=first_num, last_num=last_num)


@bill_information.route("/modify_vehicle")
def modify_vehicle():
    return render_template("modify_vehicle.html")


@bill_information.route("/validate", methods=["POST"])
def validate():
    vehicle = request.form["vehicle"]
    first_num = request.form["first_num"]
    last_num = request.form["last_num"]
    account = session['account']

    if (vehicle == '') or (first_num == '') or (last_num == '') :
        return "Your informations are incomplete!"
    
    else :
        db = current_app.config['account_database']
        collection = db.users
        collection.update_one(
            {
                "account": account
            },
            {
                "$set" : {
                    "vehicle" : vehicle,
                    "first_num" : first_num,
                    "last_num" : last_num,
                }
            }
        )
        return redirect("parking_fee")