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


def get_collab_query(variables, table, inner_joins='', conditions=''):
    """
    Generic SQL functions, especially designed to filter collaboratively
    :param variables:
        What variables get returned in the query
    :param table:
        Table from which the data is selected
    :param inner_joins:
    :param conditions:
    :return: tuple
        SQL Result
    """

    # Complile all list/tuple items
    if type(conditions) == tuple or type(conditions) == list:
        conditions = 'WHERE ' + ' AND '.join(conditions)
    elif len(conditions) > 0:
        conditions = 'WHERE ' + conditions
    if type(variables) == tuple or type(variables) == list:
        variables = ','.join(variables)
    if type(inner_joins) == tuple or type(inner_joins) == list:
        inner_joins = 'INNER JOIN ' + inner_joins.join(' INNER JOIN ')
    elif inner_joins != '':
        inner_joins = 'INNER JOIN ' + inner_joins

    # SQL standard format
    sql = f"""SELECT
                    {variables}
                FROM
                    {table}
                {inner_joins}
                    {conditions}"""

    # Executing the SQL
    cur.execute(sql)
    fetch = cur.fetchall()
    print('SQL Done')
    return fetch


#recommendation = recommendation_collaborative('59dce84ca56ac6edb4cd01fa')
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
    else:
        print(':(')

