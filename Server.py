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
import pred,food
from konlpy.tag import Kkma
from konlpy.tag import Okt

app = Flask(__name__)

#DB Connection String
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

#none json type
def on_json_loading_failed_return_dict(e):
    return {}

#access root'/'
@app.route('/')
def hello():
    print("hello")
    return jsonify(hello = 'world')

#access signUp Page
@app.route('/signUp',methods=['Post'])
def sign_up():
    #parsing json form about user's info 
    payload = request.json
#     id = 'abc134'
    id = payload['id']
    weight = payload['weight']
    height = payload['height']
    age = payload['age']
    gender = int(payload['gender'])
    activity = int(payload['activity'])
    diseaseList = payload['diseaseList'] #array
    preferredList = payload['preferredList'] #array
    nonpreferredList = payload['nonpreferredList'] #array
    
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
        
    #Kcal = height * height * if gender == 0 ? 22 : 21
    recommKcal = height*height*mul*Acmul
    
    #insert user_info
    cur.execute("INSERT INTO user_info VALUES (%s, %s, %s, %s, %s, %s, %s);",(id,str(weight),str(height),str(age),G,str(activity),str(recommKcal)))
    
    #insert user_disease
    for disease in diseaseList :
        cur.execute("INSERT INTO user_Disease VALUES (nextval('seq'), %s,%s);",(id,str(disease)))
        
    #insert user_preferredList
    for prefer in preferredList :
        print(prefer)
        cur.execute("INSERT INTO user_prefer VALUES (nextval('seq'), %s,%s);",(id,prefer))
        
    #insert user_nonpreferredList
    for nonprefer in nonpreferredList :
        print(nonprefer)
        cur.execute("INSERT INTO user_prefer VALUES (nextval('seq'), %s,%s);",(id,nonprefer))
#     conn.commit()
    
    return jsonify(hello = 'world')


#send food_info for user
@app.route('/sendImg',methods=['Post']) #Model + diary
def send_Img():
    #time
    now = datetime.now()
    id = 'abc123'
    #reqest image parsing
    imagefile = request.files["imagefile"].read()
    npimg = np.fromstring(imagefile,np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_UNCHANGED)
    image = cv2.resize(image, dsize=(112, 112), interpolation=cv2.INTER_AREA)
    try:
        image = food.test(image)
    except:
        print("error")
    x=0
    y=0
    x,y,_ = image.shape
    print(x,y)
    
    #Food image -> Food name
    array = pred.classification(image)
    value = array[0]
    cur.execute("SELECT * FROM food_info where food_name ="+"'"+value+"'"+";")
    result = cur.fetchall()
    
    print(result)
    
    #diary
    Inday = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
    Intime = str(now.hour)+":"+str(now.minute)
    cur.execute("INSERT INTO user_history VALUES (nextval('seq'), %s, %s, %s, %s);",(id,Inday,Intime,value)) 
    conn.commit()
    result[0]['food_kcal'] = float(re.sub('[,]','',result[0]['food_kcal']))
    result[0]['food_one_time'] = float(re.sub('[,]','',result[0]['food_one_time']))
    result[0]['food_carbo'] = float(re.sub('[,]','',result[0]['food_carbo']))
    result[0]['food_protein'] = float(re.sub('[,]','',result[0]['food_protein']))
    result[0]['food_fat'] = float(re.sub('[,]','',result[0]['food_fat']))
    result[0]['food_sugar'] = float(re.sub('[,]','',result[0]['food_sugar']))
    result[0]['food_salt'] = float(re.sub('[,]','',result[0]['food_salt']))
    result[0]['food_cholesterol'] = float(re.sub('[,]','',result[0]['food_cholesterol']))
    result[0]['food_fattyacid'] = float(re.sub('[,]','',result[0]['food_fattyacid']))
    result[0]['food_transfattyacid'] = float(re.sub('[,]','',result[0]['food_transfattyacid']))
    #conn.commit
    return jsonify(list = array, foodinfo = result[0])

#server send user's info to client
@app.route('/receiveInfo',methods=['Post'])
def receive_info(): 
    results = []
    Dresults = []
    Presults = []
    Nresults = []
    info = {'weight':0,'height':0,'age':0,'gender':0,'activity':0,'targetCalorie':0,
                 'diseaseList':[],'preferredList':[],'nonpreferredList':[]}
#     cur.execute("SELECT * FROM user_info where user_id = "+"'"+user_id+"'"+";")
    cur.execute("SELECT * FROM user_info where user_id = 'abc123';")
    Iresult = cur.fetchall()
    for I in Iresult :
        info['weight'] = float(I['weight'])
        info['height'] = float(I['height'])
        info['age'] = int(I['age'])
        info['gender'] = int(I['gender'])
        info['activity'] = int(I['activity'])
        info['targetCalorie'] = float(I['recommkcal'])
#     Iresult = [Iresult]
    results.append(Iresult)
    
    cur.execute("SELECT (disease) FROM user_disease where user_id = 'abc123';")
    Dresult = cur.fetchall()
    for result in Dresult :
        Dresults.append(int(result['disease']))
    info['diseaseList'] = Dresults
     
    cur.execute("SELECT (food) FROM user_prefer where user_id = 'abc123';")
    Presult = cur.fetchall()
    for result in Presult :
        Presults.append(result['food'])
    info['preferredList'] = Presults
    
    cur.execute("SELECT (food) FROM user_nonprefer where user_id = 'abc123';")
    Nresult = cur.fetchall()
    for result in Nresult :
        Nresults.append(result['food'])
    info['nonpreferredList'] = Nresults
    
    return jsonify(person = info)

#server send diary to client
@app.route('/receiveDiary',methods=['Post'])
def receive_Diary():
    #json form Dictionary
    nutrient = {'food_one_time':0,'food_kcal':0,'food_carbo':0,'food_protein':0,'food_fat':0,
                'food_sugar':0,'food_salt':0,'food_cholesterol':0,'food_fattyacid':0,'food_transfattyacid':0}
    
    cur.execute("SELECT (recommkcal) FROM user_info where user_id = 'abc123';")
    temp = cur.fetchall()
    kcal = temp[0]['recommkcal']
    nutrient['food_kcal'] = float(kcal)
     
    temp = request.json
    receiveDay = temp['day']
    
    cur.execute("SELECT * FROM user_history,food_info where user_id = 'abc123' and eat_date = "+"'"+receiveDay+"'"+" and eat_food=food_name;")
    temp = cur.fetchall()
    result = temp
    for tmp in temp :
        print(tmp)
        if tmp['eat_date'] == receiveDay :
            food = tmp['eat_food']
            cur.execute("SELECT * FROM food_info where food_name = "+"'"+food+"'"+";")
            tempK = cur.fetchall()
            nutrient['food_kcal'] =round(nutrient['food_kcal'] - float(re.sub('[,]','',tempK[0]['food_kcal'])),2)
            nutrient['food_one_time'] =round(nutrient['food_one_time'] + float(re.sub('[,]','',tempK[0]['food_one_time'])),2)
            nutrient['food_carbo'] =round(nutrient['food_carbo'] + float(re.sub('[,]','',tempK[0]['food_carbo'])),2)
            nutrient['food_protein'] =round(nutrient['food_protein'] + float(re.sub('[,]','',tempK[0]['food_protein'])),2)
            nutrient['food_fat'] =round(nutrient['food_fat'] + float(re.sub('[,]','',tempK[0]['food_fat'])),2)
            nutrient['food_sugar'] =round(nutrient['food_sugar'] + float(re.sub('[,]','',tempK[0]['food_sugar'])),2)
            nutrient['food_salt'] =round(nutrient['food_salt'] + float(re.sub('[,]','',tempK[0]['food_salt'])),2)
            nutrient['food_cholesterol'] =round(nutrient['food_cholesterol'] + float(re.sub('[,]','',tempK[0]['food_cholesterol'])),2)
            nutrient['food_fattyacid'] =round(nutrient['food_fattyacid'] + float(re.sub('[,]','',tempK[0]['food_fattyacid'])),2)
            nutrient['food_transfattyacid'] =round(nutrient['food_transfattyacid'] + float(re.sub('[,]','',tempK[0]['food_transfattyacid'])),2)            
         
    return jsonify(diary = result, value = nutrient)

@app.route('/findMenu',methods=['Post'])
def find_Menu():
    payload = request.json
    payload = payload['text']
    ret = {};
    okt = Okt();
#     divid = kkma.nouns(payload['text'])
    for noun in payload :
        cur.execute("SELECT * FROM food_info where food_name = "+"'"+noun+"'"+";")
        temp = cur.fetchall()
        if temp == None :
            divid =okt.nouns(noun);
            fix = divid[len(divid)-1]
            for several in divid :
                if several == fix :
                    continue;
                cur.execute("SELECT * FROM food_info where food_name = "+"'"+several+fix+"'"+";")
                temp = cur.fetchall()
                if temp != None :
                    break;
                cur.execute("SELECT * FROM food_info where food_name = "+"'"+several+" "+fix+"'"+";")
                temp = cur.fetchall()
                if temp != None :
                    break;
            if temp == None :
                cur.execute("SELECT * FROM food_info where food_name = "+"'%"+fix+"%'"+";")
                temp = cur.fetchall()
        if temp != None :
            ret[noun] = temp
    return jsonify(menu = ret)
    


#host='0.0.0.0' -> external access
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
