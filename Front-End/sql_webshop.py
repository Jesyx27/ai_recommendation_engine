import psycopg2

# Setting up global variables about the database
DB_NAME = 'huwebshop'
USER = 'postgres'

# password = input('Fill in the password for user \'postgres\':')
password = 'postgrespassword'
# Connection to the database is established with the defined variables
conn = psycopg2.connect(f"dbname='{DB_NAME}' user='{USER}' host='localhost' password='{password}'")
cur = conn.cursor()


def recommendation_collaborative(profile_id):
    """    Functie voor het lezen van de recommendations

    Args:
        cursor: DB cursor
        profile_id: OPTIONAL; if you want to look for a specific product _id recommendation

    Returns:
        list
    """

    query = f"""SELECT v_id, session.preferences -> 'brand' FROM session
                INNER JOIN browserid b on session._id = b.s_id
                INNER JOIN visitor v on b.v_id = v._id
                WHERE preferences IS NOT NULL
                AND v_id = '{profile_id}'"""

    cur.execute(query)
    return cur.fetchall()


def get_collaborative_information(recommend_brands):
    query = f"SELECT rec_brand.recomended_brands FROM rec_brand WHERE product_id IN {tuple(recommend_brands)}"

    cur.execute(query)
    return cur.fetchall()


def get_brand_products(brands):
    if len(brands) == 0:
        return []

    # If it is a singular element (str) turn it into a tuple
    if type(brands) != tuple and type(brands) != list:
        brands = (brands, )

    query = f"SELECT _id FROM product WHERE brand = ANY(%s)"
    cur.execute(query, tuple(brands))

    res = cur.fetchall()
    # ((0001,), (0002,), ...) => (0001, 0002, ...)
    return [p_id[0] for p_id in res]


def get_popular_products(table_name="interested_product"):
    """ Returns products in a tuple ((product_id, amount purchased), ...)
    :param table_name string the table where it pulls the
    :return tuple, i.e.: ((product_id, amount purchased), ...)
    """

    sql = f"""SELECT DISTINCT unnest(product_array), count(*) as c FROM {table_name}
    GROUP BY unnest(product_array)
    ORDER BY c DESC"""
    cur.execute(sql)
    popular_products = cur.fetchall()

    # Copy to avoid mutating the in the for-loop
    popular_products = [i[0] for i in popular_products.copy()]
    return popular_products


def get_similar_of_purchased_products(v_id="", type="brand"):
    """
    Function to get

    :param v_id: The profile ID of the current logged in user
    :param type: The column where the data is similar, OPTIONAL. Default = 'brand'
    """

    where_cls = ""

    if v_id != "":
        where_cls = f"WHERE inter.v_id = '{v_id}'"

    sql = f"""SELECT array_agg(DISTINCT p.{type}) FROM (SELECT v_id, unnest(product_array) as prod FROM interested_product) inter
                        INNER JOIN product p on inter.prod = p._id
                        {where_cls}
                        GROUP BY (inter.v_id)
        """

    cur.execute(sql)
    return cur.fetchall()


def get_collab(v_id):
    """
    Generic SQL functions, especially designed to filter collaboratively
    :return: tuple
        SQL Result
    """

    table_name = "collaborative_a"


    # SQL standard format
    sql = f"""SELECT {table_name}.products FROM {table_name}
    WHERE {table_name}.products IS NOT NULL
    AND {table_name}.v_id = '{v_id}'
"""

    # Executing the SQL
    cur.execute(sql)
    fetch = cur.fetchall()
    return fetch


def get_similar_of_product(p_id, columns):
    table_name = "product"

    columns_text = []

    for column in columns:
        columns_text.append(f"{column} = (SELECT {column} FROM {table_name} WHERE _id = '{p_id}')")

    # SQL standard format
    sql = f"""SELECT {table_name}._id from {table_name}
            WHERE {' AND '.join(columns_text)}
    """

    cur.execute(sql)
    fetch = cur.fetchall()
    categorized = [i[0] for i in fetch]
    return categorized


def get_item_with_column_value(colomn, value):
    sql = f"SELECT _id FROM product WHERE {colomn} = (SELECT {colomn} FROM product WHERE _id = '{value}')"
    cur.execute(sql)
    fetch = cur.fetchall()
    categorized = [i[0] for i in fetch]
    return categorized


def discount_recommend():
    """
    Functie voor het recommenderen van producten met een aanbieding
    """

    query = "SELECT _id\nFROM product\nWHERE price_discount IS NOT NULL\nORDER BY price_discount DESC"

    cur.execute(query)
    return cur.fetchall()


if __name__ == '__main__':
    brands = []
    recommendation = recommendation_collaborative('59dce84ca56ac6edb4cd01fa')

    if recommendation is not None:
        for i in recommendation:
            if i[1] is not None:
                brands.extend((i[1].keys()))

    if len(brands) > 0:
        collab = get_collaborative_information(brands)
        collab_brands = set()
        for i in collab:
            [collab_brands.add(j.replace('[', '').replace(']', '').strip()) for j in i[0].split(',')]

        b = get_brand_products(tuple(collab_brands))
        b = [i[0] for i in b]