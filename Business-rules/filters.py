def brand_recommend(cursor):
    """
    Functie voor het aanvullen van brand recommendations.
    
    Pseudo:
        Voor elk product_id pak alle product_id's van dezelfde brand
        en voeg deze toe aan de table rec_brand.

    Args:
        cursor: DB cursor
    
    Returns:
        String
    """

    #list voor uiteindelijke data
    finaldata = []

    #pak alle ID's van producten waarbij een brand is gegeven
    id_brand_query = "SELECT _id, brand\nFROM product\nWHERE brand IS NOT null"
    cursor.execute(id_brand_query)
    id_brand = cursor.fetchall()

    #pakt alle producten waarbij producten dezelfde brand hebben
    for item in id_brand:
        parsed_item = [i.replace('\'', '\'\'') for i in item]
        itemquery = f"SELECT _id\nFROM product\nWHERE brand = '{parsed_item[1]}'"
        cursor.execute(itemquery)
        data = cursor.fetchall()

        for parsed_item in data:
            data[data.index(parsed_item)] = parsed_item[0]

        #slaat alle producten die als enigste die brand hebben over
        if len(data) == 1:
            print(f'{parsed_item[0]}, {data} skipped')
        else:
            if parsed_item[0] in data:
                data.remove(parsed_item[0])
            data = str(data)
            data = data.replace("'", "")

            zeroth_parsed_item = parsed_item[0].replace('\'', '\'\'')
            finaldata.append(f"('{zeroth_parsed_item}', '{data}')")

    return finaldata

def others_bought(cursor, product_ids):
    """"
    Functie voor het laten zien wat anderen ook kochten bij een aangegeven product.

    Args:
        cursor: DB cursor
        product_ids: list

    Returns:
        string
    """
    preference_query = "SELECT preferences\n FROM session\nWHERE has_sale = true AND preferences IS NOT null"
    finaldata = []
    for product_id in product_ids:
        parsed_product_id = product_id.replace('\'', '\'\'')
        brand_query = f"SELECT brand\nFROM product\nWHERE _id = '{parsed_product_id}' AND brand IS NOT null"

        #pak brand van product
        cursor.execute(brand_query)
        brand = cursor.fetchone()[0]

        #pak sales
        cursor.execute(preference_query)
        sales = cursor.fetchall()

        #pak alle brand's die ook zijn gekocht naast de brand van het gegeven product
        rec_brands = []
        for sale in sales:
            try:
                if brand in sale[0]['brand']:
                   rec_brands.append(sale[0]['brand'])
            except:
                #session heeft een product zonder brand bekeken
                pass

        #gooi alle keys van rec_brands in een list
        try:
            new_rec_brands = list(rec_brands[0].keys())
        except:
            pass

        #haal degene zonder recommendations eruit
        if len(new_rec_brands) == 1:
                new_rec_brands.append('no recommendations')
    
        #haal dezelfde brand eruit
        for rec in  new_rec_brands:
            if rec == brand:
                new_rec_brands.remove(rec)
        new_rec_brands = str(new_rec_brands)
        new_rec_brands = new_rec_brands.replace("'", "")
        brand = brand.replace('\'', '\'\'')
        finaldata.append(f"('{brand}', '{new_rec_brands}')")
    return finaldata
