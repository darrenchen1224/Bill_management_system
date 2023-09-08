# 連線到 MongoDB 雲端資料庫
from pymongo.mongo_client import MongoClient
import urllib.parse  # 因密碼有 @ ，因此載入 urlib.parse 套件，解析 URL

def account_database() :
    username = urllib.parse.quote_plus('Darren')
    password = urllib.parse.quote_plus('P@ssw0rd1234')
    client = MongoClient(
        "mongodb+srv://%s:%s@mycluster.a0nsuov.mongodb.net/?retryWrites=true&w=majority" % (username, password))
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    
    db = client.account
    return db