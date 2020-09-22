import json
from ast import parse
from ast2json import ast2json

val = input("Enter python program Name: ") 

ast = ast2json(parse(open(val).read()))
print (json.dumps(ast, indent=4))

# the json file where the output must be stored
out_file = open("myfile.json", "w")

json.dump(json.dumps(ast, indent=4), out_file, indent=6)

out_file.close()


#opening AST tree in JSON format
with open("myfile.json") as f:
    data = json.load(f)
jsondata = json.loads(data)

# Defining Global variables to Store output statements
Assignments = ""
conditions = ""
loop = ""

#converting english operations to math operations
def mathOpps(argument):
    switcher = {
        "Add": "+",
        "Mult": "*",
        "Sub": "-",
        "Eq": "==",
        "Gt": ">",
        "Lt": "<",
        "GtE": ">=",
        "LtE": "<=",
        "BitAnd": "&",
        "NotEq": "!=",
        "Mod": "%",
        "Div": "/"

    }
    return switcher.get(argument, "N/A")

#Handling '_type=BinOp' Operations ex a=b+c
def BinaryOpp(BinaryTree):
    BinaryAssignment = ""
    leftOprand = ""
    rightOprand = ""
    if BinaryTree["left"]["_type"] == "BinOp":
        leftOprand += BinaryOpp(BinaryTree["left"])

    elif BinaryTree["left"]["_type"] == "Constant" or BinaryTree["left"]["_type"] == "Name":
        leftOprand = (
            str(BinaryTree["left"]["n"])
            if BinaryTree["left"]["_type"] == "Constant"
            else BinaryTree["left"]["id"]
        )

    Operation = mathOpps(BinaryTree["op"]["_type"])

    if BinaryTree["right"]["_type"] == "BinOp":
        rightOprand += BinaryOpp(BinaryTree["right"])

    elif (
        BinaryTree["right"]["_type"] == "Constant" or BinaryTree["right"]["_type"] == "Name"
    ):
        rightOprand = (
            str(BinaryTree["right"]["n"])
            if BinaryTree["right"]["_type"] == "Constant"
            else BinaryTree["right"]["id"]
        )

    BinaryAssignment += BinaryAssignment + leftOprand + Operation + rightOprand
    return BinaryAssignment

#Handling Logical operation such as (num%4) < 5
def handleLogicalCompare(ifdata):
    if ifdata["left"]['_type'] == "Constant" or ifdata["left"]['_type']=="Name":
                LHS = (
                str(ifdata["left"]["n"])
                if ifdata["left"]['_type'] == "Constant"
                else ifdata["left"]["id"] 
                )
            
    elif ifdata["left"]['_type'] == "BinOp":
                LHS=BinaryOpp(ifdata["left"])
                
    operation = mathOpps(ifdata["ops"][0]["_type"]) 

    comparator = (
            str(ifdata["comparators"][0]["n"])
            if ifdata["comparators"][0]["_type"] == "Constant"
            else ifdata["comparators"][0]["id"]
            )

            
    con= LHS + ' '+ operation+' ' + comparator 

    return con

    



#handling Logical comparisson such as (num < 5 And num > 2)
def BooleanCompare(ifdata):
    Compare=""
    leftOprand = ""
    rightOprand = ""
    if ifdata["values"][0]['_type'] == "BoolOp":
        leftOprand += BooleanCompare(ifdata["values"][0])
    elif ifdata["values"][0]['_type']=='Compare':

        if ifdata["values"][0]["comparators"][0]["_type"] == "Constant" or ifdata["values"][0]["comparators"][0]["_type"] == "Name":
            leftOprand= handleLogicalCompare(ifdata["values"][0]) 
            
            
    Oprand=ifdata['op']['_type']

    if ifdata["values"][1]['_type'] == "BoolOp":
        rightOprand += BooleanCompare(ifdata["values"][1])
    elif ifdata["values"][1]['_type']=='Compare':

        if ifdata["values"][1]["comparators"][0]["_type"] == "Constant" or ifdata["values"][1]["comparators"][0]["_type"] == "Name":
            rightOprand= handleLogicalCompare(ifdata["values"][1])
            
            
            
    
    Compare=leftOprand+' '+Oprand+' '+rightOprand
    return Compare



#handling Branch conditions for If,elif,while loop
def handleCompare(ifdata):
    con=""
    if ifdata['_type']=='Compare':
        if ifdata["comparators"][0]["_type"] == "Constant" or ifdata["comparators"][0]["_type"] == "Name":
            con+= handleLogicalCompare(ifdata)
    if ifdata['_type']=='BoolOp':
        con +=BooleanCompare(ifdata) + "\n"
    
    return con

#Handling assignment statments a=5 etc 
def SimpleAssignment(Jdata):
    global Assignments
    LHS = Jdata["targets"][0]["id"] + "="
    if Jdata["value"]["_type"] == "Constant" or Jdata["value"]["_type"] == "Name":
        Assignments += (
            LHS + str(Jdata["value"]["n"]) + "\n"
            if Jdata["value"]["_type"] == "Constant"
            else LHS + str(Jdata["value"]["id"] + "\n")
        )
    elif Jdata["value"]["_type"] == "BinOp":
        Assignments += LHS + BinaryOpp(Jdata["value"]) + "\n"

#handling lambda assignment ex a+=b
def AugAssignment(Jdata):
    global Assignments
    LHS = Jdata["target"]["id"]
    Operation=mathOpps(Jdata['op']['_type']) + '='
    if Jdata["value"]["_type"] == "Constant" or Jdata["value"]["_type"] == "Name":
        Assignments += (
            LHS + Operation + str(Jdata["value"]["n"]) + "\n"
            if Jdata["value"]["_type"] == "Constant"
            else LHS + Operation + str(Jdata["value"]["id"] + "\n")
        )
    elif Jdata["value"]["_type"] == "BinOp":
        Assignments += LHS + Operation + BinaryOpp(Jdata["value"]) + "\n"        

#handling node with type if condition
def handleIf(ifdata):
    global conditions
    global Assignments
    global handleFor
    if ifdata["_type"] == "If":
        ifBody = ifdata["body"]
        for Jdata in ifBody:
            if Jdata["_type"] == "Assign":
                SimpleAssignment(Jdata)
            elif Jdata["_type"] == "AugAssign":
                AugAssignment(Jdata)
            
            elif Jdata["_type"] == "For":
                handleFor(Jdata)
            elif Jdata["_type"] == "While":
                 handleWhile(Jdata)
            elif Jdata["_type"] == "If":
                 handleIf(Jdata)

    if ifdata["orelse"]:
        if ifdata["orelse"][0]["_type"] == "If":
            handleIf(ifdata["orelse"][0])
        elif ifdata["orelse"][0]["_type"] == "Assign":
            SimpleAssignment(ifdata["orelse"][0])

        elif ifdata["orelse"][0]["_type"] == "AugAssign":
            AugAssignment(ifdata["orelse"][0])
        elif ifdata["orelse"][0]["_type"] == "For":
            handleFor(ifdata["orelse"][0])
        elif ifdata["orelse"][0]["_type"] == "While":
                 handleWhile(ifdata["orelse"][0])
    
    if ifdata["test"]:
        conditions+=handleCompare(ifdata["test"])



#handling node with type for 
def handleFor(fordata):
    global loop
    global Assignments
    global handleIf
    if fordata["_type"] == "For":
        ifBody = fordata["body"]
        for Jdata in ifBody:
            if Jdata["_type"] == "Assign":
                SimpleAssignment(Jdata)
            elif Jdata["_type"] == "AugAssign":
                AugAssignment(Jdata)
            elif Jdata["_type"] == "If":
                handleIf(Jdata)
            elif Jdata["_type"] == "For":
                handleFor(Jdata)
            elif Jdata["_type"] == "While":
                 handleWhile(Jdata)

                

    if fordata["iter"]["_type"] == "Call":
            loop += str(fordata["target"]["id"]) + " "
            if fordata["iter"]["func"]["id"] == "range":
                loop += "in " + fordata["iter"]["func"]["id"] + " "
                fortBody = fordata["iter"]["args"]
                for pdata in fortBody:
                    if pdata["_type"] == "Constant":
                        loop += "(" + str(pdata["n"]) + ","
                    if pdata["_type"] == "Name":
                        loop += (
                            str(pdata["id"]) + "\n"
                            if pdata["_type"] == "name"
                            else pdata["id"] + ")\n"
                            )
                    elif pdata["_type"] == "BinOp":
                        loop += BinaryOpp(pdata)
                        loop += ")"  + "\n"                

#handling node with type whiile
def handleWhile(fordata):
    global loop
    global Assignments
    global handleIf
    if fordata["_type"] == "While":
        ifBody = fordata["body"]
        for Jdata in ifBody:
            if Jdata["_type"] == "Assign":
                SimpleAssignment(Jdata)
            elif Jdata["_type"] == "AugAssign":
                AugAssignment(Jdata)
            elif Jdata["_type"] == "If":
                handleIf(Jdata)
            elif Jdata["_type"] == "While":
                 handleWhile(Jdata)
            elif Jdata["_type"] == "For":
                handleFor(Jdata)

    if fordata["test"]:
        loop+=handleCompare(fordata["test"])
       

#main section to parse each Node recieved from the tree
def MainSection(jsonBody):
    for Jdata in jsonBody:
        if Jdata["_type"] == "Assign":
            SimpleAssignment(Jdata)
        elif Jdata["_type"] == "AugAssign":
            AugAssignment(Jdata)
        elif Jdata["_type"] == "If":
            handleIf(Jdata)
        elif Jdata["_type"] == "For":
            handleFor(Jdata)
        elif Jdata["_type"] == "While":
            handleWhile(Jdata)
        elif Jdata["_type"] == "FunctionDef":
            MainSection(Jdata['body'])


jsonBody = jsondata["body"]
MainSection(jsonBody)



    
        

    
        
    


print("Assignment Statements:")
print(Assignments)
print("Branch Conditions:")
print(conditions)
print("Loop Conditions:")
print(loop)


# print(type(firstindex))

# print(jsondata['body'][1])
