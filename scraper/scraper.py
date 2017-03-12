import re
from bs4 import BeautifulSoup
import urllib2
from utility import *
import pymongo
import sys


all_recipes = []
items = []
# some sites close their content for 'bots', so user-agent must be supplied
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
}

def normalize_string(string):
    return re.sub(
        r'\s+', ' ',
        string.replace(
            u'\xa0', ' ').replace(  # &nbsp;
            '\n', ' ').replace(
            '\t', ' ').strip()
    )


def processIngredient(recipe, item, amount):
	
	ingredient_collection.insert(
		{
			"recipe": recipe,
			"ingredient": item.lower(),
			"mass": amount
		}
	)

def addRecipe(name, URL, serving, count):
	recipe_collection.insert(
			{
					"recipe": name,
					"url": URL,
					"serving": serving,
					"num_ingred": count
			}
	)

def addToDatabase(name, all_ingredients, URL, serving):
	global all_recipes, items
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
	global all_recipes, items
	soup = BeautifulSoup(urllib2.urlopen(
                urllib2.Request(URL, headers=HEADERS)).read(), "html.parser")
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
	
def scrape(recipe_collection, ingredient_collection, clear_database=False):
	global all_recipes, item
	clear_database = False
	url_main = "17851"
	if len(sys.argv) > 1:
		url_main = sys.argv[1]

	if clear_database:
			recipe_collection.remove({})
			ingredient_collection.remove({})

	ingredient_collection.create_index( 'ingredient' )

	for k in list(recipe_collection.find()):
		all_recipes.append(k['recipe'])

	items = acceptedIngredients()
	single_weight = singleConversionDict()
	cup_conversion = cupConversionDict()
	ignore = ignoreIngredients()

	soup = BeautifulSoup(urllib2.urlopen(
					urllib2.Request("http://allrecipes.com/recipes/" + url_main, headers=HEADERS)).read(), "html.parser")

	topRecipes = soup.findAll('ar-save-item', {'class': "favorite"})

	#print(topRecipes[0])

	recipe_list = []

	for recipe_web in topRecipes:
		recipe_list.append(recipe_web.get("data-id"))

	#recipe_list = ['103737']

	for recipe_id in recipe_list:
		target_url = 'http://allrecipes.com/recipe/' + recipe_id
		scrap = getInfo(target_url)
		print(scrap)
		#input()

	return 'Scraped'
