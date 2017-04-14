from __future__ import division
import nextbus
import random

agency = 'sf-muni'

def howFar(firstStop, secondStop):
	# Return (boolean closeEnough, currDistance)
	# Each degree of latitude is approximately 69 miles (111 kilometers) apart.
	kmsInADegree = 111
	howManyMeters = 150
	howManyDegrees = howManyMeters / 1000 / kmsInADegree

	currDistance = abs(firstStop[0].longitude - secondStop[0].longitude) + abs(firstStop[0].latitude - secondStop[0].latitude) 
	closeEnough = currDistance < howManyDegrees

	return (closeEnough, currDistance)

allRoutes = nextbus.get_all_routes_for_agency(agency)

# routeName -> routeConfig
# "21" -> RouteConfig.stops_dict where key is 'stop_id'
routeDict = {}

# stop_id -> (StopOnRoute, [routeName list])
stopsDict = {}

for currRoute in allRoutes:
	currRouteTag = currRoute.tag
	routeConfig = nextbus.get_route_config(agency, currRouteTag)
	routeDict[currRouteTag] = routeConfig

	print currRouteTag

	for currStopId in routeConfig.stops_dict.keys():
		if currStopId in stopsDict:
			stopsDict[currStopId][1].append(currRouteTag)
		else:
			stopsDict[currStopId] = (routeConfig.stops_dict[currStopId], [currRouteTag])


# Precompute nearby stops for each stop...
nearbyStops = {}
for count, firstStop in enumerate(stopsDict.keys()):
	if count % 100 == 0:
		print count
	nearbyStopIDs = []
	for secondStop in stopsDict.keys():
		if firstStop != secondStop:
			closeEnough, distance = howFar(stopsDict[firstStop], stopsDict[secondStop])
			if closeEnough:
				nearbyStopIDs.append((secondStop, distance))
	nearbyStops[firstStop] = nearbyStopIDs

"""
Seed: a random stop

for awhile:
Pick a random line in stopsDict[randomStop]z
Ride it for a few stops (possibly randomly reversing direction?)
pick next candidate stop making sure that it has another line there to ride
"""
# start with a route
# ride X stops
# get off, look for a stop right nearby with a different line...
# 	(can't use same stop for this, because perpendicular dirs have diff stops)
currStopId = random.choice(stopsDict.keys())
lastRoute = ""

howManyBuses = 100
for count in range(howManyBuses):
	currStop = stopsDict[currStopId]
	currRouteName = lastRoute
	while lastRoute == currRouteName:
		currRouteName = random.choice(currStop[1])
	currRoute = routeDict[currRouteName]

	countOfStop = -1
	while countOfStop == -1:
		randomDirection = random.choice(currRoute.directions)

		for count, findingTheStop in enumerate(randomDirection.stops):
			if currStop[0].stop_id == findingTheStop.stop_id:
				countOfStop = count
				break

	nextStopId = ""

	failCount = 0
	while nextStopId == "":
		if random.random() < .5: #countOfStop < len(randomDirection.stops):
			moveUpwards = True
			numOfStops = int(1 + random.random() * (len(randomDirection.stops) - countOfStop))
		else:
			moveUpwards = False
			numOfStops = int(1 + random.random() * (countOfStop))

		if moveUpwards:
			newStopNum = countOfStop + numOfStops
		else:
			newStopNum = countOfStop - numOfStops

		try:
			newStopArea = randomDirection.stops[newStopNum].stop_id
			if nearbyStops[newStopArea]:
				possibleNewStopID = random.choice(nearbyStops[newStopArea])[0]
			if len(stopsDict[possibleNewStopID][1]) > 1:
				nextStopId = possibleNewStopID
		except:
			failCount += 1
			if failCount > 50:
				import pdb; pdb.set_trace()
			continue

	failCount = 0
	print "MUNI %s at %s, ride %d stops, get off at %s" % (currRouteName, currStop[0].title, numOfStops, stopsDict[nextStopId][0].title)
	currStopId = nextStopId
	lastRoute = currRouteName

print "all done byeee!"