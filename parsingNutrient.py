import requests
from bs4 import BeautifulSoup
import psycopg2

#access DB
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


#page : 2 to 840
k=0 # start : (i-2)*5
for i in range(2,840) :
    raw = requests.get('http://www.foodsafetykorea.go.kr/portal/healthyfoodlife/foodnutrient/simpleSearch.do?menu_no=2805&menu_grp=MENU_NEW03&code4=2&code2=&search_name=&page='+str(i), headers={'User-Agent':'Mozilla/5.0'}).text
    html = BeautifulSoup(raw,'html.parser')
    nutrients = html.select('div#tab2')
    
    #tag parsing
    names = nutrients[0].select('tbody > tr > th > a')
    nutrientss = nutrients[0].select('tbody > tr > td')
    Nlist =[]
    j=0 #
    count=10;
    #nutrients number parsing 
    for nutrient in nutrientss :
        if count == 10 :
            count=0 
            continue
        Nlist.append(nutrient.text.strip())
        count+=1
    try:
        #food_name parsing
        for name in names :
            cur.execute("INSERT INTO food_info VALUES ("+str(k)+", %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",(name.text.strip(),Nlist[j],Nlist[j+1],Nlist[j+2],Nlist[j+3],Nlist[j+4],Nlist[j+5],Nlist[j+6],Nlist[j+7],Nlist[j+8],Nlist[j+9]))
            j+=10
            k+=1
            print(k)
    except :
        print("error")
    conn.commit()
cur.execute("SELECT * FROM food_info;")
result = cur.fetchall()
print(result)
