import os, json, boto3, requests        # still not sure exactly how requests work
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import math

# Run flask app and cors =  browser compatibility basically
app = Flask(__name__)  #  name == special name for module
cors = CORS(app)

app.url_map.strict_slashes = False

# distance from orbiting body at closest, distance from sun
planetDict = {"Mercury": [913434000, 147003918, 3.2, 0.0000053099],  "Venus": [87913000, 141482259, 6, 0.000011502], "Earth": [0, 8.3, .0000158], "Mars": [155850000, 250816262, 12.7, 0.000022351], "Jupiter": [533220000, 858134407, 43.2, 0.00007865], "Saturn": [946470000, 1523195815, 79.3, 0.00015623], "Uranus": [1523195815, 3095090380, 159.6, 0.00031153], "Neptune": [2851900000, 4589688153, 246, 0.00047295]}

def CalcISSDist():
    # Theta has to be in radians
    # Theta(earth-p2p-angle) =  (dist in km) / 6400 km
    radiansTheta = 11500 / 6400
        # k = ?
            # Law of cosines
                # k = sqrt(81920000 - 81920000cos(Theta))
    directPath = math.sqrt(81920000 - 81920000 * math.cos(radiansTheta))
    print("direct path = ", directPath) # earth point to iss-earth point
                    # Theta = arctan(400 / k(known direct earth p2p))
    theta = math.atan(400/directPath)
                    # finalPath = 400 / sin(Theta)   
    finalPath = 400 / math.sin(theta)
    print("Final path = ", finalPath)
    return finalPath 

# routes
@app.route("/", methods = ['GET', 'POST'])
@app.route("/home", methods = ['GET', 'POST'])
def Home():
    response = requests.get('https://api.le-systeme-solaire.net/rest/bodies/')

    data = json.loads(response.content)
    objDict = dict(data)

    objDict = objDict.get("bodies")
    parsedObjDict = []
    for i in range(0, len(objDict)):
        tempBody = []

        # if earth, add # people in space, iss info? --> last
        # add weather
        tempBody.append(objDict[i].get("englishName"))
        tempBody.append(objDict[i].get("gravity"))
        tempBody.append(objDict[i].get("mass"))
        tempBody.append(objDict[i].get("meanRadius"))
        tempBody.append(objDict[i].get("density"))
        tempBody.append(objDict[i].get("escape"))
        # average distance from orbiting body
        tempBody.append((objDict[i].get("perihelion") + objDict[i].get("aphelion")) / 2)   # farthest distance to
        
        # for frontend, need to either change to dictionary or check if these exist, otherwise its out of bounds
        if(objDict[i].get("isPlanet") == True):
            planetName = objDict[i].get("englishName")
            tempBody.append(planetDict.get(planetName)[0]) # avg dist from earth in m
            tempBody.append(planetDict.get(planetName)[1]) # avg dist from earth in km
            tempBody.append(planetDict.get(planetName)[2]) # lightminutes from sun
            tempBody.append(planetDict.get(planetName)[3]) # lightyears from sun
            tempBody.append((planetDict.get(planetName)[1] * 10.989)) # football fields from earth
        parsedObjDict.append(tempBody)

    return parsedObjDict

# get descriptions for planets --> scrapped idea
@app.route("/descriptions", methods = ['GET', 'POST'])
def Descriptions():
    return "<h1> Hi :) </h1>"

# return location for user entered
# get real time iss data
# city to iss 
# radians of arc = (2(pi)(dist in km)) / (circ in km)
@app.route("/iss", methods = ['GET', 'POST'])
def Iss():
    ISS_data = requests.get('https://api.wheretheiss.at/v1/satellites/25544')

    data = json.loads(ISS_data.content)
    dataDict = dict(data)

    latLongList = []
    latLongList.append(dataDict.get("latitude"))
    latLongList.append(dataDict.get("longitude"))

    
    return jsonify(CalcISSDist) 

# Other ideas
# # people in space rn
# nearest asteroids, closest point to earth, when they get there
# donki api get news reports
# look at nasa's exoplanet archive

if __name__ == '__main__':  # true only if run directly (not through flask run, from what I can tell)
    app.run(debug=True)
