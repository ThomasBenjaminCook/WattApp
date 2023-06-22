import pandas
import statistics
import random
from datetime import datetime, timedelta
from flask import Flask, request, redirect, make_response
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

def find_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return(request.environ['REMOTE_ADDR'])
    else:
        return(request.environ['HTTP_X_FORWARDED_FOR']) # if behind a proxy

def refresh_login_count(datenumber,allips,theip):
    data_to_edit = []

    for row in allips:
        data_to_edit.append([row.uses,row.ip])

    data_refreshed = []

    for person in data_to_edit:
        person_last_used_date = int(person[0].split("_")[-1])
        person_usage_number = int(person[0].split("_")[0])
        if((person_last_used_date < datenumber) and (theip == person[-1])):
            person_usage_number += 1
            data_refreshed.append([str(person_usage_number)+"_"+str(datenumber),person[-1]])
        else:
            data_refreshed.append([str(person_usage_number)+"_"+str(person_last_used_date),person[-1]])

    for newperson in data_refreshed:
        datasource.session.query(List).filter(List.ip == newperson[-1]).update({'uses':newperson[0]})
        datasource.session.commit()

    for finalperson in data_refreshed:
        if(theip == finalperson[-1]):
            output_number = finalperson[0].split("_")[0]

    return(output_number)

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
    uses = datasource.Column(datasource.String(4096))

with open(THIS_FOLDER / "page1.txt") as f:
    lines1 = f.readlines()
lines1 = (" ").join(lines1)

with open(THIS_FOLDER / "page2.txt") as f:
    lines2 = f.readlines()
lines2 = (" ").join(lines2)

@app.route("/", methods = ["GET","POST"])
def home():

    response_object = make_response("This is a response object.")
    response_object.set_cookie("Which_User", value = 1, max_age = None, expires = None, path = '/', domain = None, 
                    secure = None, httponly = False)

    now_times = (datetime.now()).strftime("%d%m%y")
    theip = find_ip()
    youriprow = List.query.filter_by(ip=theip).first()
    if request.method == "POST":
        if youriprow is None:
            if request.form.get('action1') == 'AGL':
                iptoinsert = List(ip=theip, provider="AGL", uses=("1_"+now_times))
                datasource.session.add(iptoinsert)
                datasource.session.commit()
                return redirect("https://thomasappmaker.pythonanywhere.com/data")
            elif  request.form.get('action2') == 'Origin Energy':
                iptoinsert = List(ip=theip, provider="Origin", uses=("1_"+now_times))
                datasource.session.add(iptoinsert)
                datasource.session.commit()
                return redirect("https://thomasappmaker.pythonanywhere.com/data")
            elif  request.form.get('action3') == 'Red Energy':
                iptoinsert = List(ip=theip, provider="Red", uses=("1_"+now_times))
                datasource.session.add(iptoinsert)
                datasource.session.commit()
                return redirect("https://thomasappmaker.pythonanywhere.com/data")
            elif  request.form.get('action4') == "EnergyAustralia":
                iptoinsert = List(ip=theip, provider="EnergyAus", uses=("1_"+now_times))
                datasource.session.add(iptoinsert)
                datasource.session.commit()
                return redirect("https://thomasappmaker.pythonanywhere.com/data")
            elif  request.form.get('action5') == "ActewAGL":
                iptoinsert = List(ip=theip, provider="ActewAGL", uses=("1_"+now_times))
                datasource.session.add(iptoinsert)
                datasource.session.commit()
                return redirect("https://thomasappmaker.pythonanywhere.com/data")
            elif  request.form.get('action6') == "None of the Above":
                iptoinsert = List(ip=theip, provider="None", uses=("1_"+now_times))
                datasource.session.add(iptoinsert)
                datasource.session.commit()
                return redirect("https://thomasappmaker.pythonanywhere.com/data")
            elif  request.form.get('action7') == "I don't know":
                iptoinsert = List(ip=theip, provider="idk", uses=("1_"+now_times))
                datasource.session.add(iptoinsert)
                datasource.session.commit()
                return redirect("https://thomasappmaker.pythonanywhere.com/data")
    if(youriprow is None):
        return lines1
    else:
        return redirect("https://thomasappmaker.pythonanywhere.com/data")

@app.route("/data")
def data():
    theip = find_ip()

    allips = List.query.all()
    youriprow = List.query.filter_by(ip=theip).first()

    if youriprow is None:
        return redirect("https://thomasappmaker.pythonanywhere.com")

    usernumber = str(youriprow.id-58)
    totalusers = str(len(allips))

    now = datetime.now()

    nowplus = now + timedelta(hours = 10)
    formatted_now = nowplus.strftime("%a, %d %b, %y at %X")
    displaytime = (":").join([formatted_now.split(" ")[-1].split(":")[0],formatted_now.split(" ")[-1].split(":")[1]])

    use_times = refresh_login_count(int(now.strftime("%d%m%y")),allips,theip)

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

    implemented = stringinserter(lines2,[str(mapped-3.4),str(mapped),day1insertclassstringred+day1insertclassstringgreen+day2insertclassstringred+day2insertclassstringgreen,day1insertdivsstringred+day1insertdivsstringgreen,displaytime,totalusers,usernumber,use_times,day2insertdivsstringred+day2insertdivsstringgreen])

    return implemented