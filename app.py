# Start of web app
from flask import Flask, render_template, url_for, request, redirect, g, session
from stockly import *
import random
import txtools
import os

appName = "Stonksy"
appTag = (re.sub(r'[^a-zA-Z0-9]', '', appName)[0] + re.sub(r'[^a-zA-Z0-9]', '', appName)[math.floor(len(re.sub(r'[^a-zA-Z0-9]', '', appName))/2)] + re.sub(r'[^a-zA-Z0-9]', '', appName)[math.ceil(len(re.sub(r'[^a-zA-Z0-9]', '', appName))/2)] + re.sub(r'[^a-zA-Z0-9]', '', appName)[-1]).upper()
app = Flask(__name__)

@app.context_processor
def utility_processor():
    def getCP(type, tag):
        return get(type, tag)
    return dict(getCP=getCP)

@app.route("/")
def index():
    return render_template("index.html", appName=appName, appTag=appTag)

@app.route("/trade")
def trade():
    return render_template("trade.html", companies=companies)

@app.route("/stockPrice/<tag>")
def sP(tag):
    for comp in companies:
        if comp.tag == tag:
            company = comp
    return render_template("price.html", company=company)

@app.route("/login/<redirectUrl>", methods=["POST", "GET"])
def login(redirectUrl):
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            pd = txtools.readTxtStr(f"data/traders/{username}/password")
        except:
            return render_template("login.html", error="Incorrect username.", redirect=redirectUrl)
        else:
            if pd == password:
                session["loggedin"] = True
                session["user"] = username
                return redirect(f"/{redirectUrl}")
            else:
                return render_template("login.html", error="Incorrect password.", redirect=redirectUrl)
    else:
        return render_template("login.html", error=False, redirect=redirectUrl)

@app.route("/register/<redirectUrl>", methods=["POST", "GET"])
def register(redirectUrl):
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            pd = txtools.readTxtStr(f"data/traders/{username}/password")
        except:
            os.mkdir(f"data/traders/{username}")
            txtools.writeTxt1(f"data/traders/{username}/password", password)
            session["loggedin"] = True
            session["user"] = username
            Trader(username, 1000, [])
            return redirect(f"/{redirectUrl}")
        else:
            return render_template("login.html", error="That username is already taken!", redirect=redirectUrl)
    else:
        return render_template("register.html", redirect=redirectUrl)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/dash")
def dash():
    try:
        trader = get(1, session["user"])
    except:
        return redirect("/login")
    
    traderStocks = []
    numbers = []
    i = 0
    for company in trader.stocks:
        if trader.stocks.index(company) == i:
            traderStocks.append(get(0, company))
            numbers.append(1)
        else:
            numbers[traderStocks.index(get(0, company))] += 1
        i += 1

    netWorth = trader.cash
    for stock in trader.stocks:
        stockPrice = get(0, stock).price
        netWorth += stockPrice
    
    return render_template("dash.html", trader=trader, traderStocks=traderStocks, netWorth=netWorth, numbers=numbers)
    
@app.route("/buy<tag>", methods=["POST", "GET"])
def buy(tag):
    if request.method == "POST":
        quantity = request.form["buyRange"]
        trader = get(1, session["user"])
        company = get(0, tag)
        trader.buy(company, int(quantity))
        return redirect("/dash")
    else:
        try:
            trader = get(1, session["user"])
        except:
            return redirect(f"/login/buy{tag}")
        company = get(0, tag)
        maxPurchase = math.floor(trader.cash/company.price) if math.floor(trader.cash/company.price) <= company.open else company.open
        return render_template("buy.html", company=company, max=maxPurchase)

@app.route("/sell<tag>", methods=["POST", "GET"])
def sell(tag):
    if request.method == "POST":
        quantity = request.form["sellRange"]
        trader = get(1, session["user"])
        company = get(0, tag)
        print(len(trader.stocks))
        x = trader.sell(company, int(quantity))
        print(x)
        return redirect("/dash")
    else:
        try:
            trader = get(1, session["user"])
        except:
            return redirect(f"/login/sell{tag}")
        company = get(0, tag)
        maxPurchase = trader.stocks.count(tag)
        return render_template("sell.html", company=company, max=maxPurchase)

@app.route("/create", methods=["POST", "GET"])
def create():
    if request.method == "POST":
        receiveVol = math.floor(1000/(10000/int(request.form["volume"])))
        newComp = Company(name=request.form["name"], volume=int(request.form["volume"]), askingPrice=10000/int(request.form["volume"]), available=(int(request.form["volume"])-receiveVol), prices=[], dates=[])
        trader = get(1, session["user"])
        trader.cash -= 1000
        for i in range(receiveVol):
            trader.stocks.append(newComp.tag)
        return redirect("/trade")
    else:
        try:
            trader = get(1, session["user"])
        except:
            return redirect(f"/login/dash")
        takenTags = []
        for company in companies:
            takenTags.append(company.tag)
        return render_template("create.html", cash=trader.cash, takenTags=takenTags)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'