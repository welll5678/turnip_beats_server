import pymongo

max_number = 100

show_raw = False

try:
        conn  = pymongo.MongoClient()
        print("Connected Successfully!!")
except e:
        print("Error encountered while connecting to MongoDB:" + e)


recipesdb = conn['all_recipes_data']
recipe_collection = recipesdb['recipes']
ingredient_collection = recipesdb['ingredients']

def show_data(recipe_collection, ingredient_collection):
	recipes = dict()
	ingredients = dict()

	count = 0
	for k in list(recipe_collection.find()):
		if count < max_number:
			recipes[k['recipe']] = '    Serving: ' + k['serving'] + '   URL: ' + k['url']
			ingredients[k['recipe']] = ""
		count += 1

	for k in list(ingredient_collection.find()):
		if k['recipe'] in ingredients:
			ingredients[k['recipe']] += "\t"
			ingredients[k['recipe']] += k['ingredient']
			if not len(k['ingredient']) > 7:
				ingredients[k['recipe']] += "\t"
			ingredients[k['recipe']] += "\t"
			ingredients[k['recipe']] += str(k['mass'])
			ingredients[k['recipe']] += "\n"

	for name in recipes:
		print( name + recipes[name])
		print( ingredients[name] )

	if show_raw:
		print(list(recipe_collection.find()))
		print(list(ingredient_collection.find()))
	return 'Sweet'