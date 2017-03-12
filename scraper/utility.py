
def acceptedIngredients():
	return [item[:-1] for item in open("res/ingredients.txt")]

def ignoreIngredients():
        return [item[:-1] for item in open("res/ignore_words.txt")]

def singleConversionDict():
	item_dict = dict()
	for item in open("res/ingredients_mass.txt"):
		line = item.split(',')
		if item and item[0] != '#' and len(line)>1:
			item_dict[line[0]] = float(line[1])
	return item_dict

def cupConversionDict():
	item_dict = dict()
	for item in open("res/cup_conversion.txt"):
		line=item.split(',')
		if item and item[0] != '#' and len(line)>1:
			item_dict[line[0]] = float(line[1])
	return item_dict

def clearRecipeAndIngredient(recipe_collection, ingredient_collection):
        recipe_collection.remove({})
        ingredient_collection.remove({})
        return "Data Cleared"
