import pandas
import statistics
import random
from datetime import datetime, timedelta
from flask import Flask, request
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy

THIS_FOLDER = Path(__file__).parent.resolve()

with open(THIS_FOLDER / "style.txt") as f:
    lines = f.readlines()
lines = (" ").join(lines)

def stringinserter(string, insertables):
    array = string.split("@")
    outputarray = []
    for x in range(len(array)):
        outputarray.append(array[x])
        if x < len(insertables):
            outputarray.append(insertables[x])
    return(("").join(outputarray))

def makebox(color, side, data, inclusivity, sensitivity):

    mean = statistics.mean(data["emissions"])
    sd = statistics.stdev(data["emissions"])

    groups = []
    accumulating = 0
    groupindex = -1

    for x in range(len(data["emissions"])):
        if(color == "red"):
            if (data["emissions"][x]>(mean+(inclusivity*sd)) and accumulating == 0):
                groups.append([data["time"][x]])
                accumulating = 1
                groupindex = groupindex + 1
            elif (data["emissions"][x]>(mean+(inclusivity*sd)) and accumulating == 1):
                (groups[groupindex]).append(data["time"][x])
            else:
                accumulating = 0
        elif(color == "green"):
            if (data["emissions"][x]<(mean-(inclusivity*sd)) and accumulating == 0):
                groups.append([data["time"][x]])
                accumulating = 1
                groupindex = groupindex + 1
            elif (data["emissions"][x]<(mean-(inclusivity*sd)) and accumulating == 1):
                (groups[groupindex]).append(data["time"][x])
            else:
                accumulating = 0

    endpoints = []

    for x in groups:
        if(len(x)>sensitivity):
            endpoints.append([round(x[0]/864),round(x[-1]/864)])

    insertclasses = []
    insertdivs = []
    for pair in endpoints:
        height = pair[1]-pair[0]
        position = pair[0]
        if(side == "left" and color == "red"):
            key = random.randint(1,9999999)
            insertclasses.append(".line"+str(key)+" {position: absolute;top: "+str(position)+"%;height: "+str(height)+"%;width: 100%;background-color: red;opacity: 0.33;}")
            insertdivs.append('<div class="line'+str(key)+'"></div>')
        elif(side == "left" and color == "green"):
            key = random.randint(1,9999999)
            insertclasses.append(".line"+str(key)+" {position: absolute;top: "+str(position)+"%;height: "+str(height)+"%;width: 100%;background-color: rgba(50,255,10,0.3);}")
            insertdivs.append('<div class="line'+str(key)+'"></div>')
        elif(side == "right" and color == "green"):
            key = random.randint(1,9999999)
            insertclasses.append(".line"+str(key)+" {position: absolute;top: "+str(position)+"%;height: "+str(height)+"%;width: 100%;background-color: rgba(50,255,10,0.3);;}")
            insertdivs.append('<div class="line'+str(key)+'"></div>')
        elif(side == "right" and color == "red"):
            key = random.randint(1,9999999)
            insertclasses.append(".line"+str(key)+" {position: absolute;top: "+str(position)+"%;height: "+str(height)+"%;width: 100%;background-color: red;opacity: 0.33;}")
            insertdivs.append('<div class="line'+str(key)+'"></div>')

    insertclassstring = (("").join(insertclasses))
    insertdivsstring = (("").join(insertdivs))
    return(insertclassstring,insertdivsstring)

def dayswitch(day):
    if(day == "Mon"):
        return "mondayspredictions.csv","tuesdayspredictions.csv"
    elif(day == "Tue"):
        return "tuesdayspredictions.csv","wednesdayspredictions.csv"
    elif(day == "Wed"):
        return "wednesdayspredictions.csv", "thursdayspredictions.csv"
    elif(day == "Thu"):
        return "thursdayspredictions.csv", "fridayspredictions.csv"
    elif(day == "Fri"):
        return "fridayspredictions.csv", "saturdayspredictions.csv"
    elif(day == "Sat"):
        return "saturdayspredictions.csv", "sundayspredictions.csv"
    else:
        return "sundayspredictions.csv", "mondayspredictions.csv"

app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="ThomasAppMaker",
    password="P_R5nvjG5DV4Vd6",
    hostname="ThomasAppMaker.mysql.pythonanywhere-services.com",
    databasename="ThomasAppMaker$ipcollect",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

datasource = SQLAlchemy(app)

#Need to create table

# def ip_exists(ip):
#     conn = db.connection
#     cur = conn.cursor()
#     cur.execute("SELECT COUNT(*) FROM visitors WHERE ip = (%s)", (ip,))
#     result = cur.fetchone()[0]
#     cur.close()
#     return result > 0

@app.route("/")

class List(datasource.Model):
    __tablename__ = "ipness"
    id = datasource.Column(datasource.Integer, primary_key=True)
    ip = datasource.Column(datasource.String(4096))

datasource.create_all()

def home():
    # if request.headers.getlist("X-Forwarded-For"):
    #     ip = request.headers.getlist("X-Forwarded-For")[0]
    # else:
    #     ip = request.remote_addr
    # if not ip_exists(ip):
    #     conn = mysql.connection
    #     cur = conn.cursor()
    #     cur.execute("INSERT INTO visitors (ip) VALUES (%s)", (ip,))
    #     conn.commit()
    #     cur.close()

    # conn = mysql.connection
    # cur = conn.cursor()
    # cur.execute('SELECT COUNT(DISTINCT ip) FROM visitors')
    # result = cur.fetchone()
    # totalusers = str(result[0])
    # cur.close()

    # conn = mysql.connection
    # cur = conn.cursor()
    # cur.execute('SELECT id FROM visitors WHERE ip = (%s)', (ip,))
    # usernumber = str(cur.fetchone()).split("(")[1].split(",")[0]
    # cur.execute("SELECT * FROM visitors")
    # print(cur.fetchall())
    # cur.close()

    usernumber = "1"
    totalusers = "1"

    now = datetime.now()
    nowplus = now + timedelta(hours = 10)
    formatted_now = nowplus.strftime("%a, %d %b, %y at %X")

    displaytime = (":").join([formatted_now.split(" ")[-1].split(":")[0],formatted_now.split(" ")[-1].split(":")[1]])

    dayofweek = formatted_now.split(",")[0]
    leftfile = pandas.read_csv(THIS_FOLDER / dayswitch(dayofweek)[0])
    rightfile = pandas.read_csv(THIS_FOLDER / dayswitch(dayofweek)[1])

    time = ((formatted_now.split(" ")[5]).split(":"))
    timeseconds = (int(time[0])*60*60)+(int(time[1])*60)+(int(time[2]))
    mapped = round(timeseconds/864)

    day1insertclassstringred, day1insertdivsstringred = makebox("red","left",leftfile,0.5,3)
    day1insertclassstringgreen, day1insertdivsstringgreen = makebox("green","left",leftfile,1,3)
    day2insertclassstringred, day2insertdivsstringred = makebox("red","right",rightfile,0.5,3)
    day2insertclassstringgreen, day2insertdivsstringgreen = makebox("green","right",rightfile,1,3)

    implemented = stringinserter(lines,[str(mapped-3.4),str(mapped),day1insertclassstringred+day1insertclassstringgreen+day2insertclassstringred+day2insertclassstringgreen,day1insertdivsstringred+day1insertdivsstringgreen,displaytime,totalusers,usernumber,day2insertdivsstringred+day2insertdivsstringgreen])

    return implemented