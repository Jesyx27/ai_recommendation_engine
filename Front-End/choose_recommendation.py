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


def other_purchase(column):
    """
    Gets items from column of the items the profile with PROFILE_ID has purchased
    :returns: tuple containing brands
    """

    print(f"ALGORITHM || Tried other_purchase({column})")

    return sql_webshop.get_brand_products(sql_webshop.get_similar_of_purchased_products(PROFILE_ID))


def collab(v_id):
    print(f"ALGORITHM || Tried collab({v_id})")

    products = sql_webshop.get_collab_query(v_id)
    product_list = ()

    if len(products) > 0:
        # Unnestling
        product_list = products[0][0]
        print(product_list)
    return product_list


def choose_algorithm(choice, v_id="", move_on_if_none=True):
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
    elif choice == 1:
        recommended = other_purchase('brand')
    elif choice == 2:
        recommended = collab(v_id)
    # Idea 1; most popular products
    elif choice == 3:
        recommended = popular(10)

    if move_on_if_none and len(recommended) == 0:
        return choose_algorithm(choice + 1)
    else:
        if len(recommended) > COUNT:
            if SHUFFLE:
                random.shuffle(recommended)
            recommended = recommended[:COUNT]

        return recommended
