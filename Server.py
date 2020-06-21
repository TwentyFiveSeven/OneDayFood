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
import re
import numpy as np
#import pred,food
from konlpy.tag import Kkma
from konlpy.tag import Okt
from h5py.h5pl import size

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
    print()
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
        cur.execute("INSERT INTO user_prefer VALUES (nextval('seq'), %s,%s);",(id,prefer))
        
    #insert user_nonpreferredList
    for nonprefer in nonpreferredList :
        cur.execute("INSERT INTO user_prefer VALUES (nextval('seq'), %s,%s);",(id,nonprefer))
#     conn.commit()
    
    return jsonify(hello = 'world')


#send food_info for user

@app.route('/sendImg',methods=['Post']) #Model + diary
def send_Img():
    payload = request.json
    value = payload['food_name']
    #time
    now = datetime.now()
    """
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
    """
    cur.execute("SELECT * FROM food_info where food_name LIKE "+"'%"+value+"%'"+";")
    result = cur.fetchall()
    
    #diary
    Inday = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
    Intime = str(now.hour)+":"+str(now.minute)
    cur.execute("INSERT INTO user_history VALUES (nextval('seq'), '{}', '{}', '{}', '{}');".format(id,Inday,Intime,value))
    conn.commit()
    result[0]['food_kcal'] = float(re.sub('[,]','',result[0]['food_kcal']))
    food_kcal = result[0]['food_kcal']
    result[0]['food_one_time'] = float(re.sub('[,]','',result[0]['food_one_time']))
    result[0]['food_carbo'] = float(re.sub('[,]','',result[0]['food_carbo']))
    food_carbo = result[0]['food_carbo'] 
    result[0]['food_protein'] = float(re.sub('[,]','',result[0]['food_protein']))
    food_protein = result[0]['food_protein'] 
    result[0]['food_fat'] = float(re.sub('[,]','',result[0]['food_fat']))
    food_fat = result[0]['food_fat']
    result[0]['food_sugar'] = float(re.sub('[,]','',result[0]['food_sugar']))
    food_sugar = result[0]['food_sugar']
    result[0]['food_salt'] = float(re.sub('[,]','',result[0]['food_salt']))
    food_salt =result[0]['food_salt'] 
    result[0]['food_cholesterol'] = float(re.sub('[,]','',result[0]['food_cholesterol']))
    food_cholesterol =result[0]['food_cholesterol'] 
    result[0]['food_fattyacid'] = float(re.sub('[,]','',result[0]['food_fattyacid']))
    food_fattyacid = result[0]['food_fattyacid'] 
    result[0]['food_transfattyacid'] = float(re.sub('[,]','',result[0]['food_transfattyacid']))
    food_transfattyacid = result[0]['food_transfattyacid']
    array = []
    #check food record
    cur.execute("SELECT * FROM Intake where date = '"+Inday+"' and user_id = 'abc123';")
    Frecord = cur.fetchall()
    if bool(Frecord) != False :
        food_kcal = food_kcal + Frecord[0]['sum_kcal']
        food_carbo = food_carbo + Frecord[0]['sum_carbo']
        food_protein = food_protein + Frecord[0]['sum_protein']
        food_fat = food_fat  + Frecord[0]['sum_fat']
        food_sugar = food_sugar + Frecord[0]['sum_sugar']
        food_salt = food_salt + Frecord[0]['sum_salt']
        food_cholesterol = food_cholesterol + Frecord[0]['sum_cholesterol']
        food_fattyacid = food_fattyacid + Frecord[0]['sum_fattyacid']
        food_transfattyacid = food_transfattyacid + Frecord[0]['sum_transfattyacid']
        cur.execute("UPDATE Intake SET sum_kcal = {} ,sum_carbo = {}, sum_protein = {}, sum_fat = {} , sum_sugar = {} , sum_salt = {} , sum_cholesterol = {}, sum_fattyacid = {}, sum_transfattyacid = {} WHERE date = '{}' and user_id = 'abc123';".format(food_kcal,food_carbo,food_protein,food_fat,food_sugar,food_salt,food_cholesterol,food_fattyacid,food_transfattyacid,Inday))
#         cur.execute("UPDATE Intake SET food_kcal = "+str(food_kcal)+",food_carbo = "+str(food_carbo)+", food_protein = "+str(food_protein)+", food_fat = "+str(food_fat)+", food_sugar = "+str(food_sugar)+", food_salt = "+str(food_salt)+", food_cholesterol = "+str(food_cholesterol)+", food_fattyacid = "+str(food_fattyacid)+", food_transfattyacid = "+str(food_transfattyacid)+" WHERE date = '"+Inday+"' and user_id = 'abc123';")
        conn.commit()
    else :
        cur.execute("INSERT INTO Intake VALUES (nextval('seq'), '{}', '{}', {}, {}, {}, {}, {}, {}, {}, {}, {});".format(Inday,'abc123',food_kcal,food_carbo,food_protein,food_fat,food_sugar,food_salt,food_cholesterol,food_fattyacid,food_transfattyacid))
        conn.commit()
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
    cur.execute("SELECT * FROM Intake where date = '"+reciveDay+"' and user_id = 'abc123';")
    Val = cur.fetchall()
    cur.execute("SELECT * FROM user_history,food_info where user_id = 'abc123' and eat_date = "+"'"+receiveDay+"'"+" and eat_food=food_name;")
    temp = cur.fetchall()
    result = temp
    nutrient['food_kcal'] = Val[0]['sum_kcal']
    nutrient['food_one_time'] = 0 
    nutrient['food_carbo'] =Val[0]['sum_carbo']
    nutrient['food_protein'] =Val[0]['sum_protein']
    nutrient['food_fat'] =Val[0]['sum_fat']
    nutrient['food_sugar'] =Val[0]['sum_sugar']
    nutrient['food_salt'] =Val[0]['sum_salt']
    nutrient['food_cholesterol'] = Val[0]['sum_cholesterol']
    nutrient['food_fattyacid'] =Val[0]['sum_fattyacid']
    nutrient['food_transfattyacid'] =Val[0]['sum_transfattyacid']            
    return jsonify(diary = result, value = nutrient)

@app.route('/findMenu',methods=['Post'])
def find_Menu():
    now = datetime.now()
    index = 0;
    payload = request.json
    payload = payload['text']
    food_list = []
    indexList = []
    color_list = []
    ret = {};
    okt = Okt();
    for noun in payload :
        cur.execute("SELECT * FROM food_info where food_name = '{}';".format(noun))
        temp = cur.fetchall()
        if bool(temp) == False :
            divid =okt.nouns(noun)
            fix = divid[len(divid)-1]
            for serveral in divid :
                if serveral == fix :
                    continue
                cur.execute("SELECT * FROM food_info where food_name = '{}';".format(serveral+fix))
                temp = cur.fetchall()
                if bool(temp) != False :
                    indexList.append(index)
                    food_list.append(temp[0])
                    break
                cur.execute("SELECT * FROM food_info where food_name = '{}';".format(serveral+' '+fix))
                temp = cur.fetchall()
                if bool(temp) != False :
                    indexList.append(index)
                    food_list.append(temp[0])
                    break
            if bool(temp) == False :
                cur.execute("SELECT * FROM food_info where food_name LIKE '%{}';".format(fix))
                temp = cur.fetchall()
            if bool(temp) == False :
                index +=1
                continue
            else :
                indexList.append(index)
                food_list.append(temp[0])
        else :
            indexList.append(index)
            food_list.append(temp[0])
        index +=1
    Inday = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
    cur.execute("SELECT * FROM user_history,food_info where user_id = 'abc123' and eat_date = "+"'"+Inday+"'"+" and eat_food=food_name;")
    temp = cur.fetchall()
    result = temp
    Inday = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
    cur.execute("SELECT * FROM Intake where date = '"+Inday+"' and user_id = 'abc123';")
    Val = cur.fetchall()
    if bool(Val) == False :
        food_kcal = 0.0
        food_carbo =0.0
        food_protein=0.0
        food_fat = 0.0
        food_sugar = 0.0
        food_salt = 0.0
        food_cholesterol = 0.0
        food_fattyacid = 0.0
        food_transfattyacid = 0.0
    else :
        food_kcal = Val[0]['sum_kcal']
        food_carbo =Val[0]['sum_carbo']
        food_protein=Val[0]['sum_protein']
        food_fat =Val[0]['sum_fat']
        food_sugar =Val[0]['sum_sugar']
        food_salt =Val[0]['sum_salt']
        food_cholesterol = Val[0]['sum_cholesterol']
        food_fattyacid =Val[0]['sum_fattyacid']
        food_transfattyacid =Val[0]['sum_transfattyacid']
    #상대적으로 ?
    #현재 남은 kcal에서 /3 값보다 큰지 작은지 ? or kcal이 초과라면 가능 kcal에서 /3
    #병을 갖고 있으면 간? 이런거 salt, 콜레스테롤 문제면 cholesterol
    cur.execute("SELECT * FROM user_info where user_id = 'abc123';")
    temp = cur.fetchall()
    MaxKcal = float(temp[0]['recommkcal'])
    middle_list = []
    limit_dic = {'food_kcal': MaxKcal, 'food_carbo' : 130.0, 'food_salt' : 2000.0, 'food_fat' : 51.0, 'food_sugar' : 30.0, 'food_cholesterol' : 300.0, 'food_transfattyacid' : 2.0,'food_protein' : 80.0, 'food_fattyacid' : 20.0}
    disease_dic = {1 : ['food_salt'], 2 : ['food_fat','food_kcal'], 3 : ['food_cholesterol','food_salt'], 4 : ['food_carbo','food_sugar','food_fat']}
    cur.execute("SELECT * FROM user_disease where user_id = 'abc123';")
    temp = cur.fetchall()
    disease_list = []
    for K in temp :
        disease_list.append(int(K['disease']))
    user_disease = []
    for Food,Tindex in zip(food_list,indexList) :
        Value = 0.0
        danger = 0
        for nutrient in Food :
            if nutrient == 'id' or nutrient == 'food_name' or nutrient == 'food_one_time' :
                continue 
            Value = Value + (float(Food[nutrient].replace(',','')) - limit_dic[nutrient]/3)/(limit_dic[nutrient]/3)
        for disease in disease_list :
            check_list = disease_dic[disease]
            for nutrient in check_list :
                if float(Food[nutrient].replace(',','')) > limit_dic[nutrient]/2 :
                    danger = 1
        middle_list.append((Value,Tindex,danger))
    sorted(middle_list, key = lambda middle : middle[0])
    final_list = []
    level = 0;
    size = int(len(middle_list)/3)
    count = 0;
    for i in range(0,len(middle_list)) :
        if count == size :
            level +=1
            count =0
        if middle_list[i][2] ==1 :
            final_list.append((middle_list[i][1],2))
        else :
            final_list.append((middle_list[i][1],level))
        count +=1
    return jsonify(a = indexList, b =final_list)


#host='0.0.0.0' -> external access
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
