import sql_webshop

global COUNT
global PROFILE_ID

def popular():
    """
    :returns Most popular products as taken from `interested_product` table
    """
    print("ALGORITHM || Tried popular()")
    recommended = sql_webshop.get_popular_products()
    if len(recommended) > COUNT:
        recommended = recommended[:COUNT]

    return recommended


def other_purchase_brand():
    print("ALGORITHM || Tried other_purchase_brand()")
    return sql_webshop.get_brand_products(sql_webshop.get_brands_of_purchased_products(PROFILE_ID))


def choose_algorithm(choice, move_on_if_none=True):
    """
    :param choice Choice of what algorithm to use (temp)
    :param move_on_if_none OPTIONAL, whether to move on to the next algorithm
     if the chosen one doesn't return any items
    """
    recommended = []

    if choice == 1:
        recommended = other_purchase_brand()
    elif choice == 2:
        recommended = popular()

    if move_on_if_none and len(recommended) == 0:
        return choose_algorithm(choice + 1)
    else:
        return recommended
