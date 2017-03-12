import pymongo

max_number = 100

show_raw = False

try:
        conn  = pymongo.MongoClient()
        print("Connected Successfully!!")
except e:
        print("Error encountered while connecting to MongoDB:" + e)


recipesdb = conn['all_recipes_data']
inventory_collection = recipesdb['inventory']

recipes = dict()
ingredients = dict()

print("\n============DATABASE============\n")
count = 0
for k in list(inventory_collection.find()):
	if count < max_number:
		print(k['item'] + ': \t\t' + str(k['mass']))
	else:
		break
	count += 1



