import pymongo

recipesdb = conn['all_recipes_data']
old_recommend_collection = recipesdb['old_recommend']
def clear_recent(old_recommend_collection)
    old_recommend_collection.remove({})
    return 'Cleared recent recommendations'
