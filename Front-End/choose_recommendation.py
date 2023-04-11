import random

import sql_webshop
import itertools
global COUNT
global PROFILE_ID
global SHUFFLE

def popular(max_len):
    """
    :param top_len How long th popular list is, this is implemented for the shuffle function
    :return Most popular products as taken from `interested_product` table
    """
    print("ALGORITHM || Tried popular()")
    recommended = sql_webshop.get_popular_products()
    if len(recommended) >= max_len:
        return recommended[:max_len]
    else:
        return recommended


def other_purchase(type):
    """
    Gets brands of the items the profile with PROFILE_ID has purchased
    :returns tuple containing brands
    """

    print("ALGORITHM || Tried other_purchase_category()")
    print('CATEGORY', sql_webshop.get_similar_of_purchased_products(PROFILE_ID, type))
    print('PROFILE_ID', PROFILE_ID)

    return sql_webshop.get_brand_products(sql_webshop.get_similar_of_purchased_products(PROFILE_ID))


def choose_algorithm(choice, move_on_if_none=True):
    """
    :param choice Choice of what algorithm to use (temp)
    :param move_on_if_none OPTIONAL, whether to move on to the next algorithm
     if the chosen one doesn't return any items
    """
    recommended = []

    # Idea 3; previously purchased categories
    if choice == 0:
        recommended = other_purchase('category')
    # Idea 4; previously purchased brands
    if choice == 1:
        recommended = other_purchase('brand')
    # Idea 1; most popular products
    elif choice == 2:
        recommended = popular(10)

    if move_on_if_none and len(recommended) == 0:
        return choose_algorithm(choice + 1)
    else:
        if len(recommended) > COUNT:
            if SHUFFLE:
                random.shuffle(recommended)
            recommended = recommended[:COUNT]

        return recommended
