import pymongo
recipesdb = conn['all_recipes_data']
recipe_collection = recipesdb['old_recommend']

def show_recent(old_recommend)
        k = list(recipe_collection.find()):
        return k

