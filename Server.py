# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from flask import request
from flask import Resource, Api
from flask_restful import reqparse
from Tools.scripts.serve import app
import psycopg2

app = Flask(__name__)
api = Api(app)

user = 'postgres'
password = 'jkr124'
host = 'localhost'
dbname = 'postgres'
port='5432'
conn_string = "dbname={dbname} user={user} host={host} password={password} port={port}"\
                            .format(dbname=dbname,
                                    user=user,
                                    host=host,
                                    password=password,
                                    port=port)
try:
    conn = psycopg2.connect(conn_string)
except :
    print("error")
cur = conn.cursor()

def on_json_loading_failed_return_dict(e):
    return {}

@app.route('/signUp',methods=['Post'])
def sign_up():
    payload = request.json
#     user_id = payload[""]
#     user_password = payload[""]
    id = "abc123"
    weight = double(payload["weight"])
    height = double(payload["height"])
    age = payload["age"]
    gender = int(payload["gender"])
    activity = int(payload["activity"])
    DiseaseList = payload["DiseaseList"] #array
    preferredList = payload["preferredList"] #array
    nonpreferredList = payload["nonpreferredList"] #array
    #Kcal = height * height * if gender == 0 ? 22 : 21
    
    mul = 22
    G = "Man"
    if gender == 1 :
        mul = 21
        G = "Woman"
    
    Acmul = 30
    if activity == 1 :
        Acmul = 35
    elif activity == 2 : 
        Acmul = 40
    
    recommKcal = height*height*mul*Acmul
    cur.execute("INSERT INTO user_info VALUES (%s, %s, %s, %s, %s, %s, %s);",(id,str(weight),str(height),str(age),str(gender),G,str(activity),str(recommKcal)))
    for Disease in DiseaseList :
        cur.execute("INSERT INTO user_Disease VALUES (nextval('seq'), %s,%s);",(id,str(Disease)))
    for preferred in preferredList :
        cur.execute("INSERT INTO user_prefer VALUES (nextval('seq'), %s,%s);",(id,prefer))
    for nonprefer in nonpreferredList :
         cur.execute("INSERT INTO user_prefer VALUES (nextval('seq'), %s,%s);",(id,nonprefer))
    conn.commit()
    
    return 

@app.route('/sendImg',methods=['Post']) #Model + diary
def send_Img():
    return 

@app.route('/receiveDiary',methods=['Post'])
def receive_Diary():
    return

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
