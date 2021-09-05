from flask import Flask, render_template, request
from sawo import createTemplate, verifyToken
import mysql.connector

import json
import os
import LinearP
API_KEY = "67f7c7df-4430-49c7-ae39-1876732a708e"

cnx = mysql.connector.connect(user='root', password='15w60ps',
                              host='localhost',
                              database='acumen')  
cursor = cnx.cursor()

app = Flask(__name__)
# using flask = True genrates flask template
createTemplate("templates/partials", flask=True)
Recipe = {}
load = ''
loaded = 0
global loggedIn
loggedIn = False

def setPayload(payload):
    global load
    load = payload


def setLoaded(reset=False):
    global loaded
    if reset:
        loaded = 0
    else:
        loaded += 1


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login_page")
def login_page():
    setLoaded()
    setPayload(load if loaded < 2 else '')
    sawo = {
        "auth_key": API_KEY,
        "to": "login",
        "identifier": "email"
    }
    print(loggedIn)
    if loggedIn:
        return render_template("dashboard.html")

    else:
        return render_template("login.html", sawo=sawo, load=load)





@app.route("/login", methods=["POST", "GET"])
def login():

    payload = json.loads(request.data)["payload"]
    setLoaded(True)
    setPayload(payload)
    if(verifyToken(payload)):
        print("Logged in")
        status = 200
        global loggedIn
        loggedIn = True
        print(loggedIn)

    else:
        print("Failed login")
        status = 404
    return {"status": status}
@app.route("/data_entry", methods=["POST", "GET"])
def data_entry():
    cursor.execute("select * from `product info`;")
           

    data = cursor.fetchall()
    return render_template("dataEntryPage.html",data=data)

@app.route("/raw_material", methods=["POST", "GET"])
def raw_material():

    return render_template("rawMaterial.html")

@app.route("/add_product", methods=["POST", "GET"])
def add_product():
    msg = "Fill in the basic details about your product here"
    if request.method == 'POST':
        name      = request.form['name']
        hours     = request.form['hours']
        mrp       = request.form['mrp']

        cursor.execute("INSERT INTO  `product info`  VALUES (NULL,'{}','{}','{}');".format(name,mrp,hours))
        cnx.commit()
        msg = "Product added successfully !!"
    return render_template("add-product.html",msg = msg)


@app.route("/calculate", methods=["POST", "GET"])
def calculate():
    Payload = {}  
    if request.method == 'POST':
        budget  = int(request.form['budget'])
        hours   = int(request.form['hours'])
        Payload = LinearP.Solve(budget,hours)
    return render_template("Calci.html", Payload = Payload)

@app.route("/ProductDeet/<Product_Id>", methods=['GET', 'POST'])
def ProductDeet(Product_Id):
    cursor.execute("SELECT * FROM `product info` where `User ID` = {} ;".format(Product_Id))

    data = cursor.fetchall()
    cursor.execute("SELECT name FROM `recipe` where `id` = {} ;".format(Product_Id))
    recipe = cursor.fetchall()
    if len(recipe) == 0:
        Recipe = {}
    else:
        
        Recipe = LinearP.Str_To_Dic(recipe[0][0])
    cursor.execute("SELECT name,Price FROM `raw materials`;")
    Cost = cursor.fetchall()
    costs = {}
    for i in Cost:
        costs[i[0]] = i[1]
    final = []
    count = 0
    for i in Recipe:
        count+=1
        final.append([count,i,costs[i],Recipe[i]])
    return render_template('productDeets.html', data=data[0],final = final)

if __name__ == '__main__':
    app.run()
