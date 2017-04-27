from flask import Flask
from flask import jsonify
from flask import request
from flask import abort
from pop_inventory.pop_inv import popInventory
import tensorflow as tf
import pymongo
import logging
import sys

#from scraper.scraper import scrape
from recommendations.recommend import recommend_recipes
from classifier.label_image import *
import os

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
DB_NAME = 'heroku_w26bwb75'  
DB_HOST = 'ds129030.mlab.com'
DB_PORT = 29030
DB_USER = 'heroku_w26bwb75'
DB_PASS = 'i8jeeblr2rai5ab8h8n4ts7to3'

connection = pymongo.MongoClient(DB_HOST, DB_PORT)
db = connection[DB_NAME]
db.authenticate(DB_USER, DB_PASS)
sess = tf.Session()

sess, sm_tensor = initialize_session(sess, 'res/apple.jpg')
rejection_threshold = 0.5
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

    if 'item' in request.json:

    ######################
        # THIS IS THE ACTUAL THING YOU SEND
        item = request.json['item']
        mass = request.json['mass']
    ###########
        if item != 'Error':
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
        return jsonify({'result':'Error not put in inventory'})
    elif 'inventory' in request.json:
        inv_list = []
        ######################
            # THIS IS THE ACTUAL THING YOU SEND
        inv_diff = request.json['inventory']
        ###########
        for ingred in inv_diff:            
            item = ingred['item']
            mass = ingred['mass'] 
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
            inv_list.append({'item' : inv_item['item'], 'mass' : inv_item['mass']})
        return jsonify({'inventory':inv_list})
    abort(404)
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

##############################
    #THIS IS WHAT YOU SEND ME
    num_servings = request.json['servings']
#################################
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
            if ing['ingredient'] not in missing_items[recipe]:
                ingred_list.append({'item': ing['ingredient'], 'mass': ing['mass']*num_servings})
        missing_ingred_list = []
        for item in missing_items[recipe]:
            missing_ingred_list.append({'item':item, 'mass': missing_items[recipe][item]})
        missing_rec_list.append({'name' : rec['recipe'], 'url' : rec['url'], 'ingredients': ingred_list, 'shoppinglist':missing_ingred_list})
    return jsonify({'complete': rec_list, 'incomplete': missing_rec_list})

@app.route('/threshold', methods=['POST'])
def adjust_threshold():
    global rejection_threshold
    if 'threshold' in request.json:
        threshold = float(request.json['threshold'])
        if threshold < 1 and threshold >= 0:
            rejection_threshold = threshold
            print("Threshold")
    return jsonify({'threshold':rejection_threshold})

@app.route('/classify', methods=['POST'])
def classify():
    f = request.files['file']
    image_data = f.read()
    label = classify_image(sess, sm_tensor, image_data, rejection_threshold)
    print("Object classified as {} with threshold {}".format(label,rejection_threshold))
    return jsonify({'label': label,'threshold':rejection_threshold})

@app.route('/scrape', methods=['POST'])
def scrape_for_recipes():
    recipes = db.recipes
    ingredients = db.ingredients
#    print(scrape(recipes,ingredients))
    return get_all_recipes()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(port==5000))