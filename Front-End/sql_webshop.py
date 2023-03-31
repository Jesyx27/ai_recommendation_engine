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

    print(query)

    cur.execute(query)
    return cur.fetchall()


def get_brands(brands):
    query = f"SELECT _id FROM product WHERE brand IN {tuple(brands)}"
    cur.execute(query)
    print(query)
    return cur.fetchall()


#recommendation = recommendation_collaborative('59dce84ca56ac6edb4cd01fa')
if __name__ == '__main__':
    brands = []
    recommendation = recommendation_collaborative('59dce84ca56ac6edb4cd01fa')

    if recommendation is not None:
        for i in recommendation:
            if i[1] is not None:
                brands.extend((i[1].keys()))

    collab = get_collaborative_information(brands)
    collab_brands = set()
    for i in collab:
        [collab_brands.add(j.replace('[', '').replace(']', '').strip()) for j in i[0].split(',')]

    b = get_brands(tuple(collab_brands))
    b = [i[0] for i in b]
