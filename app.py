from flask import Flask
from flask import jsonify
from flask import request
from pop_inventory.pop_inv import popInventory
import pymongo
#from scraper.scraper import scrape
from recommendations.recommend import recommend_recipes
import os

app = Flask(__name__)

DB_NAME = 'heroku_w26bwb75'  
DB_HOST = 'ds129030.mlab.com'
DB_PORT = 29030
DB_USER = 'heroku_w26bwb75'
DB_PASS = 'i8jeeblr2rai5ab8h8n4ts7to3'

connection = pymongo.MongoClient(DB_HOST, DB_PORT)
db = connection[DB_NAME]
db.authenticate(DB_USER, DB_PASS)

#Get full inventory
@app.route('/inventory', methods=['GET'])
def get_all_inventory_items():
    inventory = db.inventory
    output = []
    for s in inventory.find():
        output.append({'item' : s['item'], 'mass' : s['mass']})
    return jsonify({'inventory' : output})

#Modify single item
@app.route('/inventory/', methods=['POST'])
def modify_inventory_item():
    inventory = db.inventory
    item = request.json['item']
    mass = request.json['mass']
    table_item = inventory.find_one({'item' : item})
    if table_item:
        item_id = inventory.update({
        'item': table_item['item']
        },{
        '$set': {
            'mass': table_item['mass'] + mass
        }
        }, upsert=False, multi=False)
    else:
        item_id = inventory.insert({'item': item, 'mass': mass})

    inv_item = inventory.find_one({'item': item})
    output = {'item' : inv_item['item'], 'mass' : inv_item['mass']}
    return jsonify({'result' : output})

#Populate inventory with default stuff.
@app.route('/pop_inventory', methods=['POST'])
def PI():
    inventory = db.inventory
    popInventory(inventory)
    return get_all_inventory_items()

#reset the inventory
@app.route('/reset_inventory', methods=['POST'])
def reset_inventory():    
    inventory = db.inventory
    inventory.remove({})
    return 'Reset the inventory'

#show_all_recipes
@app.route('/all_recipes', methods=['GET'])
def get_all_recipes():
    recipes = db.recipes
    ingredients = db.ingredients
    recipe_list = []
    ingredient_list = []
    for s in recipes.find():
        recipe_list.append({'recipe' : s['recipe'], 'url' : s['url'], 'serving': s['serving'],'num_ingredients': s['num_ingred']})    
    for s in ingredients.find():
        ingredient_list.append({'recipe' : s['recipe'], 'ingredient' : s['ingredient'], 'mass': s['mass']})
    return jsonify({'recipes' :  recipe_list, 'ingredients' : ingredient_list})

#actual recommended recipes, assuming single database.
@app.route('/recommended_recipes', methods=['POST'])
def get_recommended_recipes():
    inventory_collection = db.inventory
    num_servings = request.json['servings']
    recipe_collection = db.recipes
    ingredient_collection = db.ingredients
    old_recommend_collection = db.old_recommendations
    recommended_list, missing_recipes, missing_items = recommend_recipes(inventory_collection,recipe_collection,ingredient_collection,old_recommend_collection, num_servings)
    
    rec_list = []
    #compiling the good ol recommendation list.
    for rec in recommended_list:
        ingred_list = []
        for ing in ingredient_collection.find({'recipe': rec}):
            ingred_list.append({'item': ing['ingredient'], 'mass': ing['mass']*num_servings})
        rec2 = recipe_collection.find_one({'recipe': rec})
        rec_list.append({'name' : rec2["recipe"], 'url' : rec2['url'], 'ingredients': ingred_list})
    
    missing_rec_list = []
    #compiling the incomplete ones
    for recipe in missing_recipes:
        ingred_list = []
        rec = recipe_collection.find_one({'recipe':recipe})
        for ing in ingredient_collection.find({'recipe': recipe}):
            ingred_list.append({'item': ing['ingredient'], 'mass': ing['mass']*num_servings})
        missing_ingred_list = []
        for item in missing_items[recipe]:
            missing_ingred_list.append({'item':item, 'mass': missing_items[recipe][item]})
        missing_rec_list.append({'name' : rec['recipe'], 'url' : rec['url'], 'ingredients': ingred_list, 'shoppinglist':missing_ingred_list})
    return jsonify({'complete': rec_list, 'incomplete': missing_rec_list})
#scraper.

'''
@app.route('/scrape', methods=['POST'])
def scrape_for_recipes():
    recipes = db.recipes
    ingredients = db.ingredients
    print(scrape(recipes,ingredients))
    return get_all_recipes()
'''
if __name__ == '__main__':
    app.run(debug=True)