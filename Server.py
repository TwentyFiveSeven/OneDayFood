# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from flask import request
from flask_restful import Resource
from flask_restful import reqparse
from Tools.scripts.serve import app
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
from decimal import Decimal
import ipython_genutils
import re,cv2
import numpy as np

app = Flask(__name__)

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
cur = conn.cursor(cursor_factory = RealDictCursor)

def on_json_loading_failed_return_dict(e):
    return {}

@app.route('/')
def hello():
    print("hello")
    return jsonify("hello")

@app.route('/signUp',methods=['Post'])
def sign_up():
    print(request)
    payload = request.json
    print(payload)
    id = 'abc125'
    weight = payload['weight']
    height = payload['height']
    age = payload['age']
    gender = int(payload['gender'])
    activity = int(payload['activity'])
    diseaseList = payload['diseaseList'] #array
    preferredList = payload['preferredList'] #array
    nonpreferredList = payload['nonpreferredList'] #array
    #Kcal = height * height * if gender == 0 ? 22 : 21
    
    mul = 22
    G = 'Man'
    if gender == 2 :
        mul = 21
        G = 'Woman'
    
    Acmul = 25
    if activity == 2 :
        Acmul = 30
    elif activity == 3 : 
        Acmul = 35
    else :
        Acmul = 40
    
    recommKcal = height*height*mul*Acmul
    cur.execute("INSERT INTO user_info VALUES (%s, %s, %s, %s, %s, %s, %s);",(id,str(weight),str(height),str(age),G,str(activity),str(recommKcal)))
    for disease in diseaseList :
        cur.execute("INSERT INTO user_Disease VALUES (nextval('seq'), %s,%s);",(id,str(disease)))
    for prefer in preferredList :
        print(prefer)
        cur.execute("INSERT INTO user_prefer VALUES (nextval('seq'), %s,%s);",(id,prefer))
    for nonprefer in nonpreferredList :
        print(nonprefer)
        cur.execute("INSERT INTO user_prefer VALUES (nextval('seq'), %s,%s);",(id,nonprefer))
#     conn.commit()
    
    return jsonify(hello = 'world')


@app.route('/sendImg',methods=['Post']) #Model + diary
def send_Img():
    now = datetime.now()
    
    imagefile = request.files['imagefile'].read()
    npimg = np.fromstring(imagefile,np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_UNCHANGED)
#     cv2.IMSHOW('adsf',imagefile)
#     cv2.waitKey(0)
    id = 'abc123'
    value = "해물칼국수"
    cur.execute("SELECT * FROM food_info where food_name ="+"'"+value+"'"+";")
    result = cur.fetchall()
    print(result)
     
    #diary
    Inday = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
    Intime = str(now.hour)+":"+str(now.minute)
    cur.execute("INSERT INTO user_history VALUES (nextval('seq'), %s, %s, %s, %s);",(id,Inday,Intime,value))
    
    #conn.commit
    return jsonify(result)

@app.route('/receiveInfo',methods=['Post'])
def receive_info():
    results = []
    Dresults = []
    Presults = []
    Nresults = []
    cur.execute("SELECT * FROM user_info where user_id = 'abc123';")
    Iresult = cur.fetchall()
    Iresult = [Iresult]
    results.append(Iresult)
    cur.execute("SELECT (disease) FROM user_disease where user_id = 'abc123';")
    Dresult = cur.fetchall()
    for result in Dresult :
        Dresults.append(result)
    cur.execute("SELECT (food) FROM user_prefer where user_id = 'abc123';")
    Presult = cur.fetchall()
    for result in Presult :
        Presults.append(result)
    cur.execute("SELECT (food) FROM user_nonprefer where user_id = 'abc123';")
    Nresult = cur.fetchall()
    for result in Nresult :
        Nresults.append(result)
    results.append(Dresults)
    results.append(Presults)
    results.append(Nresults)
    return jsonify(results)
 
@app.route('/receiveDiary',methods=['Post'])
def receive_Diary():
    nutrient = {'food_one_time':0,'food_kcal':0,'food_carbo':0,'food_protain':0,'food_fat':0,'food_sugar':0,'food_salt':0,'food_cholesterol':0,'food_fattyacid':0,'food_transfattyacid':0}
    cur.execute("SELECT (recommkcal) FROM user_info where user_id = 'abc123';")
    temp = cur.fetchall()
    kcal = temp[0]['recommkcal']
    nutrient['food_kcal'] = float(kcal)
     
    temp = request.json
    receiveDay = temp['day']
    
    cur.execute("SELECT * FROM user_history where user_id = 'abc123' and eat_date = "+"'"+receiveDay+"'"+";")
    temp = cur.fetchall()
    result = temp
    for tmp in temp :
        if tmp['eat_date'] == receiveDay :
            food = tmp['eat_food']
            cur.execute("SELECT * FROM food_info where food_name = "+"'"+food+"'"+";")
            tempK = cur.fetchall()
            nutrient['food_kcal'] -= float(re.sub('[,]','',tempK[0]['food_kcal']))
            nutrient['food_one_time'] += float(re.sub('[,]','',tempK[0]['food_one_time']))
            nutrient['food_carbo'] += float(re.sub('[,]','',tempK[0]['food_carbo']))
            nutrient['food_protain'] += float(re.sub('[,]','',tempK[0]['food_protain']))
            nutrient['food_fat'] += float(re.sub('[,]','',tempK[0]['food_fat']))
            nutrient['food_sugar'] += float(re.sub('[,]','',tempK[0]['food_sugar']))
            nutrient['food_salt'] += float(re.sub('[,]','',tempK[0]['food_salt']))
            nutrient['food_cholesterol'] += float(re.sub('[,]','',tempK[0]['food_cholesterol']))
            nutrient['food_fattyacid'] += float(re.sub('[,]','',tempK[0]['food_fattyacid']))
            nutrient['food_transfattyacid'] += float(re.sub('[,]','',tempK[0]['food_transfattyacid']))            
    
    ret = []
    for rett in result :
        ret.append(rett)
    ret.append(nutrient)
    
    return jsonify(ret)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
