import pymongo
import sys


def singleConversionDict():
        item_dict = dict()
        for item in open("res/ingredients_mass.txt"):
                line = item.split(',')
                if item and item[0] != '#' and len(line)>1:
                        item_dict[line[0]] = float(line[1])
        return item_dict

def addInventory(name, mass,inventory):
        inventory.insert(
                {
                        "item": name,
                        "mass": mass
                }
        )
def popInventory(inventory):
        single_weight = singleConversionDict()

        for item in open("res/inventory_file.txt"):
                line = item.split(",")
                if line[0].lower() in single_weight:
                        mass = single_weight[line[0]] * float(line[1])
                        if mass != 0.0:
                                addInventory(line[0], mass,inventory)

