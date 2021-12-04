import os

# For internal use
def nR(list):
    list2 = []
    for el in list:
        el = el.replace("\n", "", 1)
        list2.append(el)
    
    return list2

def writeTxt1(path, value):
    f = open(f"{path}.txt", "w")
    f.write(str(value))
    f.close()

def readTxtStr(path):
    f = open(f"{path}.txt", "r")
    values = f.readlines()
    value = """"""
    for line in values:
        value += f"""{line}"""
    f.close()
    return value

def writeTxtList(path, value):
    f = open(f"{path}.txt", "w")
    f.write("")
    f.close()
    f = open(f"{path}.txt", "a")
    for item in value:
        f.write(str(item) + "\n")
    f.close()

def readTxtList(path):
    f = open(f"{path}.txt", "r")
    value = f.readlines()
    f.close()
    return nR(value)

def delTxt(path):
    os.remove(f"{path}.txt")