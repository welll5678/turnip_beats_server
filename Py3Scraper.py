import re

from bs4 import BeautifulSoup
from urllib import request
import pymongo
import sys

clear_database = False
url_main = "17851"

# some sites close their content for 'bots', so user-agent must be supplied
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
}

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

try:
        conn  = pymongo.MongoClient()
        print("Connected Successfully!!")
except e:
        print("Error encountered while connecting to MongoDB:" + e)

if len(sys.argv) > 1:
	url_main = sys.argv[1]

recipesdb = conn['restdb']
recipe_collection = recipesdb['recipes']
ingredient_collection = recipesdb['ingredients']
ingredient_collection.create_index( 'ingredient' )

if clear_database:
        recipe_collection.delete_many({})
        ingredient_collection.delete_many({})

all_recipes = []

for k in list(recipe_collection.find()):
	all_recipes.append(k['recipe'])

items = acceptedIngredients()
single_weight = singleConversionDict()
cup_conversion = cupConversionDict()
ignore = ignoreIngredients()

print(ignore)

def normalize_string(string):
    return re.sub(
        r'\s+', ' ',
        string.replace(
            '\xa0', ' ').replace(  # &nbsp;
            '\n', ' ').replace(
            '\t', ' ').strip()
    )


def processIngredient(recipe, item, amount):
	
	ingredient_collection.insert_one(
		{
			"recipe": recipe,
			"ingredient": item.lower(),
			"mass": amount
		}
	)

def addRecipe(name, URL, serving, count):
	recipe_collection.insert_one(
                {
                        "recipe": name,
                        "url": URL,
                        "serving": serving,
			"num_ingred": count
                }
        )

def addToDatabase(name, all_ingredients, URL, serving):
	count = 0
	for i in all_ingredients:
		for ingredient in items:
			if ingredient.lower() in i.lower():
				
				ounce = re.search('(?<=\()[0-9]+.*[0-9]*(?= *ounce)', i)
				amount = 0.
				if ounce:
					amount = float(ounce.group()) * 28.35
				else:
					cup = re.search('[0-9]+ *[0-9]*/*[0-9]*(?= *cup)', i)
					if cup and ingredient.lower() in cup_conversion:
						digits = cup.group().split(" ")
						val = 0
						fract = digits[0]
						if len(digits) == 2:
							fract = digits[1]
							val += float(digits[0])
						fract_list = fract.split("/")
						if len(fract_list)==2:
							val += float(fract_list[0])/float(fract_list[1])
						elif fract:
						
							val += float(fract)
						amount = cup_conversion[ingredient.lower()] * val
					elif cup:
						continue
					else:
						b_ignore = False
						for ignore_i in ignore:
							if ignore_i in i.lower():
								b_ignore = True
						if b_ignore:
							continue
						amount =  int(re.search(r'\d+', i).group())
						for single_item in single_weight:
							if single_item.lower() in i.lower():
								amount = single_weight[single_item] * amount
				
				processIngredient(name, ingredient, amount)
				count += 1
				break
	if count > 0:
		addRecipe(name, URL, serving, count)

def getInfo(URL):
	soup = BeautifulSoup(request.urlopen(
                request.Request(URL, headers=HEADERS)).read(), "html.parser")
	name = soup.find('h1').get_text()

	if name in all_recipes:
		return

	ingredients_html = soup.findAll('li', {'class': "checkList__line"})
	ingredient_list = [ normalize_string(ingredient.get_text()) 
	for ingredient in ingredients_html
	 if ingredient.get_text(strip=True) not in ('Add all ingredients to list', '','Advertisement') ]
	serving_html = soup.findAll('meta', {'id': "metaRecipeServings"})
	serving = serving_html[0].get("content")
	addToDatabase(name, ingredient_list, URL, serving)
	all_recipes.append(name)
	return ingredient_list

soup = BeautifulSoup(request.urlopen(
                request.Request("http://allrecipes.com/recipes/" + url_main, headers=HEADERS)).read(), "html.parser")

topRecipes = soup.findAll('ar-save-item', {'class': "favorite"})

#print(topRecipes[0])

recipe_list = []

for recipe_web in topRecipes:
	recipe_list.append(recipe_web.get("data-id"))

#recipe_list = ['103737']

for recipe_id in recipe_list:
	print(recipe_id)
	target_url = 'http://allrecipes.com/recipe/' + recipe_id
	scrap = getInfo(target_url)
	#print(scrap)
	#input()


