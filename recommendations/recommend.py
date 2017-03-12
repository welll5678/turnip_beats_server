from __future__ import print_function
import pymongo
from collections import Counter
import random

def  recommend_recipes(inventory_collection,recipe_collection,ingredient_collection,old_recommend_collection, num_servings, num_recommendations=5):
	cnt = Counter()
	old_recipes = []
	for recipe in old_recommend_collection.find():
		old_recipes.append(recipe['recipe'])


	missing_weight = dict()

	missing_items = dict()

	inventory = list(inventory_collection.find())

	inventory_items = [x['item'] for x in inventory]

	for recipe in list(ingredient_collection.find()): #{'ingredient': inventory['item'] } )):#, "mass": { '$lt': inventory['mass'] } } ) ):
		if recipe['ingredient'] in inventory_items and (recipe['mass']*num_servings) <= inventory[inventory_items.index(recipe
	['ingredient'])]['mass']:	
			cnt[recipe['recipe']] += 1
		else:
			if not recipe['recipe'] in missing_weight:
				missing_weight[recipe['recipe']] = 0
			if recipe['recipe'] not in missing_items:
				missing_items[recipe['recipe']] = dict()
			if recipe['ingredient'] in inventory_items:
				val = (recipe['mass'] * num_servings) - inventory[inventory_items.index(recipe['ingredient'])]['mass']
				missing_weight[recipe['recipe']] += val
				missing_items[recipe['recipe']][recipe['ingredient']] = val
			else:
				missing_weight[recipe['recipe']] += (recipe['mass'] *num_servings)
				missing_items[recipe['recipe']][recipe['ingredient']] = (recipe['mass']*num_servings)

	match_list = []

	for recipe in list(recipe_collection.find()):
		if recipe['num_ingred'] == cnt[recipe['recipe']]:
			match_list.append(recipe['recipe'])

	random.shuffle(match_list)

	recommended_list = []

	for recipe in match_list:
		if not recipe in old_recipes:
			recommended_list.append(recipe)
			if not len(recommended_list) < num_recommendations:
				break

	if not len(recommended_list) == num_recommendations:
		for recipe in match_list:
				if not recipe in recommended_list:
						recommended_list.append(recipe)
						if not len(recommended_list) < num_recommendations:
								break

	missing = num_recommendations - len(recommended_list)
	missing_recipe = []

	if missing > 0:
		for key, value in sorted([(v,k) for k,v in missing_weight.items()]):
			missing_recipe.append(value)
			missing -= 1
			if missing == 0:
				break

	old_recommend_collection.remove({})

	for recipe in recommended_list:
		old_recommend_collection.insert(
			{
				"recipe": recipe
			}
		)
	return recommended_list, missing_recipe, missing_items
