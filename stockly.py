import math
import re
import txtools
from os import listdir
from os.path import isfile, join, isdir
import time
import random

companies = []
traders = []

class Error:
    def __init__(self, message:str):
        self.message = message

def codeToMessage(code):
    codes = {
        0: Error("Company doesn't have enough open stocks."),
        1: Error("Trader doesn't have enough funds."),
        2: Error("Trader doesn't own enough stocks.")
        }

def storeTrader(trader):
    stocks = ""
    for stock in trader.stocks:
        stocks += "," + stock
    traderData = (f"{trader.name},{trader.cash}{stocks}")
    txtools.writeTxt1(f"data/traders/{trader.name}/data", traderData)

class Trader:
    def __init__(self, name:str, balance:float, stocks:list):
        self.name = name
        self.cash = float(balance)
        self.stocks = stocks
        storeTrader(self)
        traders.append(self)
    def buy(self, stock, volume:int):
        if stock.price*volume <= self.cash:
            availability = stock.buy(volume)
            if availability != 0:
                for i in range(volume):
                    self.cash -= stock.prices[-2]
                    self.stocks.append(stock.tag)
                storeTrader(self)
            else:
                return availability
        else:
            return 1
    def sell(self, stock, volume:int):
        numStock = self.stocks.count(stock.tag)
        if numStock >= volume:
            stock.sell(volume)
            for i in range(volume):
                self.stocks.remove(stock.tag)
            self.cash += volume*stock.price
            storeTrader(self)
        else:
            return 2

def storeCompany(company):
    prices = ""
    for price in company.prices:
        prices += "," + str(price)
    companyData = f"{company.name},{company.tag},{company.volume},{company.net},{company.open}{prices}"
    txtools.writeTxt1(f"data/companies/{company.tag}", companyData)

class Company:
    def __init__(self, name:str, volume:int, askingPrice:float, available:int, prices:list):
        self.startingPrice = askingPrice
        self.name = name
        name = re.sub(r'[^a-zA-Z0-9]', '', name)
        if len(name) < 2:
            name = name + "NX"
        self.tag = (name[0] + name[math.floor(len(name)/2)] + name[math.ceil(len(name)/2)] + name[-1]).upper()
        self.volume = volume
        self.net = volume * askingPrice
        self.price = askingPrice
        self.open = available
        self.url = f"/stockPrice/{self.tag}"
        self.prices = prices
        if len(self.prices) == 0:
            self.prices.append(self.price)
        storeCompany(self)
        companies.append(self)
    def buy(self, volume:int):
        if volume <= self.open:
            self.net += volume*self.price
            self.price = self.net/self.volume
            self.open -= volume
            self.prices.append(self.price)
        else:
            return 0
        storeCompany(self)
    def sell(self, volume:int):
        self.net -= volume*self.price
        self.price = self.net/self.volume
        self.open += volume
        self.prices.append(self.price)
        storeCompany(self)

def updateComps():
    onlyfiles = [f for f in listdir("data/companies") if isfile(join("data/companies", f))]
    for fN in onlyfiles:
        fN = fN.replace(".txt", "")
        companyDataList = txtools.readTxtStr(f"data/companies/{fN}").split(",")
        prices = []
        i = 0
        for item in companyDataList:
            if i > 4:
                prices.append(float(item))
            i += 1
        Company(companyDataList[0], int(companyDataList[2]), float(companyDataList[3])/float(companyDataList[2]), int(companyDataList[4]), prices)

def updateTraders():
    onlydirs = [f for f in listdir("data/traders") if isdir(join("data/traders", f))]
    for dN in onlydirs:
        dataFile = [f for f in listdir(f"data/traders/{dN}") if isfile(join(f"data/traders/{dN}", f)) and f != "password.txt"][0]
        fN = dataFile.replace(".txt", "")
        tDL = txtools.readTxtStr(f"data/traders/{dN}/{fN}").split(",")
        listOfStocks = []
        i = 0
        for stock in tDL:
            if i < 2:
                pass
            else:
                listOfStocks.append(stock)
            i += 1
        Trader(tDL[0], tDL[1], listOfStocks)

def get(type:int, tag:str):
    if type == 0:
        for company in companies:
            if company.tag == tag:
                return company
    elif type == 1:
        for trader in traders:
            if trader.name == tag:
                return trader
    return None

updateComps()
updateTraders()