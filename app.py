import pandas
import statistics
import random
from datetime import datetime, timedelta
from flask import Flask, request, redirect
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy

THIS_FOLDER = Path(__file__).parent.resolve()

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

class List(datasource.Model):
    __tablename__ = "ipness"
    id = datasource.Column(datasource.Integer, primary_key=True)
    ip = datasource.Column(datasource.String(4096))
    provider = datasource.Column(datasource.String(4096))

with open(THIS_FOLDER / "page1.txt") as f:
    lines1 = f.readlines()
lines1 = (" ").join(lines1)

with open(THIS_FOLDER / "page2.txt") as f:
    lines2 = f.readlines()
lines2 = (" ").join(lines2)

@app.route("/", methods = ["GET","POST"])
def home():
    if request.method == "POST":
        if request.headers.getlist("X-Forwarded-For"):
            theip = request.headers.getlist("X-Forwarded-For")[0]
        else:
            theip = request.remote_addr

        youriprow = List.query.filter_by(ip=theip).first()

        if youriprow is None:
            if request.form.get('action1') == 'AGL':
                iptoinsert = List(ip=theip, provider="AGL")
                datasource.session.add(iptoinsert)
                datasource.session.commit()
                return redirect("https://thomasappmaker.pythonanywhere.com/data", code=302)
            elif  request.form.get('action2') == 'Origin':
                iptoinsert = List(ip=theip, provider="Origin")
                datasource.session.add(iptoinsert)
                datasource.session.commit()
                return redirect("https://thomasappmaker.pythonanywhere.com/data", code=302)
            elif  request.form.get('action3') == 'Red':
                iptoinsert = List(ip=theip, provider="Red")
                datasource.session.add(iptoinsert)
                datasource.session.commit()
                return redirect("https://thomasappmaker.pythonanywhere.com/data", code=302)
        else:
            return redirect("https://thomasappmaker.pythonanywhere.com/data", code=302)

    return lines1

@app.route("/data")
def data():
    if request.headers.getlist("X-Forwarded-For"):
        theip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        theip = request.remote_addr

    allips = List.query.all()
    youriprow = List.query.filter_by(ip=theip).first()

    if youriprow is None:
        return redirect("https://thomasappmaker.pythonanywhere.com", code=302)

    usernumber = str(youriprow.id-22)
    totalusers = str(len(allips))

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

    implemented = stringinserter(lines2,[str(mapped-3.4),str(mapped),day1insertclassstringred+day1insertclassstringgreen+day2insertclassstringred+day2insertclassstringgreen,day1insertdivsstringred+day1insertdivsstringgreen,displaytime,totalusers,usernumber,day2insertdivsstringred+day2insertdivsstringgreen])

    return implemented