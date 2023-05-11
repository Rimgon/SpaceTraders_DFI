import requests, json, time
from time import sleep

#Read in the token from a file I can gitignore. Sorry, you can't have mine ;)
#if you want to use this code for some reason, just create the file "token.cfg" which contains only the string that is your token.
token_file = open("token.cfg","r")
token = token_file.read()
token_file.close()


SPEEDS = ("DRIFT", "CRUISE", "BURN", "STEALTH")
#DRIFT is good for low fuel situations. CRUISE and BURN are just fast and faster. STEALTH uses the same fuel as CRUISE but travels slower, while being harder to detect

#Error codes, for error handling later: https://docs.spacetraders.io/api-guide/response-errors

#register my account/agent
'''url = "https://api.spacetraders.io/v2/register"
#headers = {"Content-Type": "application/json"}		#this line was redundant, I guess it knows that it's dealing with json
payload = {"symbol": "RIMGON","faction": "COSMIC"}
r = requests.post(url, data=payload)'''


'''
#sample code for pagination
payload = {"page": 2}
return requests.get(url, headers=head, params=payload)
'''


# Some style standards (shocking)
# methods that only return information and don't alter anything are to be named get_xxx
# methods that are run once and perform a fairly boolean operation (toggles, firing, etc) are to be named do_xxx
# methods that set values or otherwise do things more complex than in a do_xxx method are to be named set_xxx



def showR(r):
	"""Pass in the object returned by a request and this function will convert the json into a Python dictionary and print it out neatly"""
	json_object = json.loads(r.text)
	print(json.dumps(json_object, indent=2))


def show(j):
	"""Pass in a python dictionary from a json file and prints it nicely"""
	print(json.dumps(j, indent=2))


def get_agent(t=token):
	"""Gets your agent info, including symbol, id, headquarters, and credits"""
	url = "https://api.spacetraders.io/v2/my/agent"
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.get(url, headers=head).text)


def get_factions(t=token):
	"""Get a list of factions and their details"""
	url = "https://api.spacetraders.io/v2/factions"
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.get(url, headers=head).text)


#Horribly incomplete, only shows one page, no formatting. Also I think this is static, and so I could just save the results locally, and eventually graph them
def get_systems(t=token):
	"""Gets the massive list of systems, subsystems, waypoints, and coordinates"""
	url = "https://api.spacetraders.io/v2/systems"
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.get(url, headers=head).text)


def get_system_waypoints(system,t=token):
	"""Pass in a systemSymbol string to get details about the system it represents"""
	url = f"https://api.spacetraders.io/v2/systems/{system}/waypoints"
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.get(url, headers=head).text)

#The docs call out the "traits" flag as important. "MARKETPLACE" and "SHIPYARD" traits are notable especially.
def get_waypoint_info(system,waypoint,t=token):
	"""Pass in a systemSymbol and a waypointSymbol to get details of the waypoint, including traits"""
	url = f"https://api.spacetraders.io/v2/systems/{system}/waypoints/{waypoint}"
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.get(url, headers=head).text)




#Shipyard Commands

#Please generalize and deprecate this for the love of god
def get_shipyard_ships(system,waypoint,t=token):
	"""List the ships available at a shipyard"""
	url = f"https://api.spacetraders.io/v2/systems/{system}/waypoints/{waypoint}/shipyard"
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.get(url, headers=head).text)


def do_buy_ship(waypoint,shipType,t=token):
	"""Purchase the named ship from a shipyard at the provided waypoint"""
	url = "https://api.spacetraders.io/v2/my/ships"
	head = {"Authorization": ("Bearer " + t)}
	payload = {"shipType": shipType,"waypointSymbol": waypoint}
	return json.loads(requests.post(url,headers=head,data=payload).text)



#Contract Commands

def get_current_contracts(t=token):
	"""Get a list of current contracts"""
	url = "https://api.spacetraders.io/v2/my/contracts"
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.get(url, headers=head).text)

#I don't think this works for more than one contract, oops
def show_contracts(t=token):
	"""Displays a list of current contracts in a nice, neat format"""
	j = get_current_contracts(t)
	if(j["data"][0]["type"]=="PROCUREMENT"):		#expand this as I encounter more contracts
		action_word = "deliver"
	else:
		print("{j['data'][0]['type']} is a new type of contract, please add it to the show_contracts function")

	display_text = (f'{j["data"][0]["factionSymbol"]} {j["data"][0]["type"]} CONTRACT\n'
		f'ID: {j["data"][0]["id"]}\n'
		f'ACCEPTED? {j["data"][0]["accepted"]}\tFULFILLED? {j["data"][0]["fulfilled"]}\n'
		f'{action_word} {j["data"][0]["terms"][action_word][0]["unitsFulfilled"]}/{j["data"][0]["terms"][action_word][0]["unitsRequired"]} of {j["data"][0]["terms"][action_word][0]["tradeSymbol"]} to {j["data"][0]["terms"][action_word][0]["destinationSymbol"]}\n'
		f'UP-FRONT: ${j["data"][0]["terms"]["payment"]["onAccepted"]}\tON COMPLETION: ${j["data"][0]["terms"]["payment"]["onFulfilled"]}\n'
		f'DEADLINE: {j["data"][0]["terms"]["deadline"]}\n'
		f'EXPIRES ON: {j["data"][0]["expiration"]}\n')
	print(display_text)


def do_accept_contract(contract,t=token):
	"""Accept a contract of a given contractID"""
	url = f"https://api.spacetraders.io/v2/my/contracts/{contract}/accept"
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.post(url, headers=head).text)


def get_contract_details(contract,t=token):
	"""Get the details of a given contractID"""
	url = f"https://api.spacetraders.io/v2/my/contracts/{contract}"
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.get(url, headers=head).text)


def show_contract_details(contract,t=token):
	"""Displays the details of a specified contract in human-readable format"""
	j = get_contract_details(contract,t)
	if(j["data"]["type"]=="PROCUREMENT"):		#expand this as I encounter more contracts
		action_word = "deliver"
	else:
		print("{j['data']['type']} is a new type of contract, please add it to the show_contract_details function")

	display_text = (f'{j["data"]["factionSymbol"]} {j["data"]["type"]} CONTRACT\n'
		f'ID: {j["data"]["id"]}\n'
		f'ACCEPTED? {j["data"]["accepted"]}\tFULFILLED? {j["data"]["fulfilled"]}\n'
		f'{action_word} {j["data"]["terms"][action_word][0]["unitsFulfilled"]}/{j["data"]["terms"][action_word][0]["unitsRequired"]} of {j["data"]["terms"][action_word][0]["tradeSymbol"]} to {j["data"]["terms"][action_word][0]["destinationSymbol"]}\n'
		f'UP-FRONT: ${j["data"]["terms"]["payment"]["onAccepted"]}\tON COMPLETION: ${j["data"]["terms"]["payment"]["onFulfilled"]}\n'
		f'DEADLINE: {j["data"]["terms"]["deadline"]}\n'
		f'EXPIRES ON: {j["data"]["expiration"]}\n')
	print(display_text)


def do_contract_deliver(contract,ship,symbol,count,t=token):
	"""Deliver the provided quantity of the specified item from the specified ship for the specified contract"""
	url = f'https://api.spacetraders.io/v2/my/contracts/{contract}/deliver'
	head = {"Authorization": ("Bearer " + t)}
	payload = {"shipSymbol": ship, "tradeSymbol": symbol, "units": count}
	return json.loads(requests.post(url, headers=head, data=payload).text)


#Navigation & Ship commands

def get_ships(t=token):
	"""Gets the list of all ships the agent owns"""
	url = f'https://api.spacetraders.io/v2/my/ships'
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.get(url, headers=head).text)

def get_ship_info(ship,t=token):
	"""Gets the json pertaining to a given ship"""
	url = f'https://api.spacetraders.io/v2/my/ships/{ship}'
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.get(url, headers=head).text)


def show_ship(ship,t=token):
	"""Displays the important parts of a ship's status in human-readable format"""
	j = get_ship_info(ship,t)
	if(j["data"]["nav"]["waypointSymbol"] != j["data"]["nav"]["route"]["destination"]["symbol"]):
		dest_text = f'en route to {j["data"]["nav"]["route"]["destination"]["symbol"]}'
	else:
		dest_text = ''
	display_text = (f'Ship {j["data"]["symbol"]} {j["data"]["nav"]["status"]} @ {j["data"]["nav"]["waypointSymbol"]} {dest_text}\n'
		f'Flight mode: {j["data"]["nav"]["flightMode"]}\t Fuel: {j["data"]["fuel"]["current"]}/{j["data"]["fuel"]["capacity"]}\t Cargo: {j["data"]["cargo"]["units"]}/{j["data"]["cargo"]["capacity"]}')
	print(display_text)


def show_ship_cargo(ship,t=token):
	"""Gets the json pertaining to a given ship, then prunes it to be just the cargo"""
	j = get_ship_status(ship,t)
	display_text =  f'Ship {j["data"]["symbol"]} cargo:\n{j["data"]["cargo"]}\n'
	print(display_text)


def show_ship_fuel(ship,t=token):
	"""Gets the json pertaining to a given ship, then prunes it to be just the fuel"""
	j = get_ship_status(ship,t)
	display_text =  f'Ship {j["data"]["symbol"]}: {j["data"]["fuel"]["current"]}/{j["data"]["fuel"]["capacity"]} Fuel'
	print(display_text)


def get_ship_system(ship,t=token):
	"""Gets the json pertaining to a given ship, then prunes it to be just the system data"""
	j = get_ship_status(ship,t)
	return j["data"]["nav"]["systemSymbol"]


def get_ship_waypoint(ship,t=token):
	"""Gets the json pertaining to a given ship, then prunes it to be just the waypoint data"""
	j = get_ship_status(ship,t)
	return j["data"]["nav"]["waypointSymbol"]


def do_orbit(ship,t=token):
	"""Idempotent function to undock and move the ship passed in by argument into orbit"""
	url = f'https://api.spacetraders.io/v2/my/ships/{ship}/orbit'
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.post(url, headers=head).text)


def do_dock(ship,t=token):
	"""Idempotent function to dock the ship passed in by argument"""
	url = f'https://api.spacetraders.io/v2/my/ships/{ship}/dock'
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.post(url, headers=head).text)


def set_flight_mode(ship,mode,t=token):
	"""Sets the passed ship to the speed specified. Use the SPEEDS tuple when calling the function"""
	url = f'https://api.spacetraders.io/v2/my/ships/{ship}/nav'
	head = {"Authorization": ("Bearer " + t)}
	payload = {"flightMode": mode}
	return json.loads(requests.patch(url, headers=head, data=payload).text)


def set_destination(ship,waypoint,t=token):
	"""Sets the ship's destination to the provided waypoint, and starts flying there"""
	url = f'https://api.spacetraders.io/v2/my/ships/{ship}/navigate'
	head = {"Authorization": ("Bearer " + t)}
	payload = {"waypointSymbol": waypoint}
	return json.loads(requests.post(url, headers=head, data=payload).text)


def set_warp(ship,system,t=token):
	"""Sets the ship's warp drive to the destination system. Not instant, consumes fuel"""
	return 0


def set_jump(ship,system,t=token):
	"""Set the ship's jump drive to the destination system. Instant, consumes 1 antimatter"""
	return 0




#Ship Functions (other than navigation)


def do_transfer(shipSource,shipDestination,tradeSymbol,count,t=token):
	"""Move cargo from one ship to another at the same location"""
	url = f"https://api.spacetraders.io/v2/my/ships/{shipSource}/transfer"
	head = {"Authorization": ("Bearer " + t)}
	payload = {"tradeSymbol": tradeSymbol, "units": count, "shipSymbol": shipDestination}
	return json.loads(requests.post(url,headers=head, data=payload).text)


def do_refuel(ship,t=token):
	"""Refuels the specified ship, if there is fuel available at the location"""
	url = f"https://api.spacetraders.io/v2/my/ships/{ship}/refuel"
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.post(url,headers=head).text)


def do_extract(ship,survey="",t=token):
	"""Extract the resources from the ship's current location. Has a cooldown"""
	url = f'https://api.spacetraders.io/v2/my/ships/{ship}/extract'
	head = {"Authorization": ("Bearer " + t)}

	#if we're trying to use a survey, include that, otherwise don't
	if(survey != ""):
		payload = {"survey": survey}
		return json.loads(requests.post(url, headers=head, data=payload).text)
	else:
		return json.loads(requests.post(url, headers=head).text)


def do_survey(ship,t=token):
	"""Survey the current location to get a list of locations for resource extraction. Requires surveying equipment"""
	url = f'https://api.spacetraders.io/v2/my/ships/{ship}/survey'
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.post(url, headers=head).text)


def do_refine(ship,resource,t=token):
	"""Refine IRON, COPPER, SILVER, GOLD, ALUMINUM, PLATINUM, URANITE, MERITIUM, or FUEL from raw resources"""
	url = f'https://api.spacetraders.io/v2/my/ships/{ship}/refine'
	head = {"Authorization": ("Bearer " + t)}
	payload = {"produce": resource}
	return json.loads(requests.post(url, headers=head, data=payload).text)



#Wallstreet Bets Commands

#read the docs for this, seriously. https://docs.spacetraders.io/game-concepts/markets
def get_market(system,waypoint,t=token):
	"""Get the market info of a waypoint in a system. You must have a ship at the waypoint for this to work"""
	url = f'https://api.spacetraders.io/v2/systems/{system}/waypoints/{waypoint}/market'
	head = {"Authorization": ("Bearer " + t)}
	return json.loads(requests.get(url, headers=head).text)


def do_sell(ship,item,count,t=token):
	"""Sell the provided quantity of the specified item from the specified ship"""
	url = f'https://api.spacetraders.io/v2/my/ships/{ship}/sell'
	head = {"Authorization": ("Bearer " + t)}
	payload = {"symbol": item, "units": count}
	return json.loads(requests.post(url, headers=head, data=payload).text)
#TODO: Implement a "sell all" function


def do_purchase(ship,item,count,t=token):
	"""buy the provided quantity of the specified item for the specified ship"""
	url = f'https://api.spacetraders.io/v2/my/ships/{ship}/purchase'
	head = {"Authorization": ("Bearer " + t)}
	payload = {"symbol": item, "units": count}
	return json.loads(requests.post(url, headers=head, data=payload).text)




def starterContractDeliver(ship,cargoSpace):
	#once we arrive at the destination, run this
	do_dock(ship)
	do_contract_deliver("clhfgy9cg19pls60df8umn14g",ship,"ALUMINUM_ORE",cargoSpace)
	do_refuel(ship)
	do_orbit(ship)
	set_destination(ship,"X1-DF55-17335A")
	#"X1-DF55-17335A" asteroid field
	#"X1-DF55-20250Z" station to deliver to

def starterContractPurchase(ship,cargoSpace):
	#back at the asteroid field, do this
	do_dock(ship)
	do_refuel(ship)
	do_purchase(ship,"ALUMINUM_ORE",cargoSpace)
	do_orbit(ship)
	set_destination(ship,"X1-DF55-20250Z")


def starterContractAuto(ship,cargoSpace,trips):
	for i in range(0,trips):
		starterContractDeliver(ship,cargoSpace)
		sleep(20)
		starterContractPurchase(ship,cargoSpace)
		sleep(20)
		show_ship(ship)
	print("Done!")


print("All functions loaded")