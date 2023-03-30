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


def get_collaborative_information(brands):
    query = "SELECT * FROM rec_brand"

    print(query)

    cur.execute(query)
    return cur.fetchall()

q = recommendation_collaborative('59ddc2e2a56ac6edb4ea005e')
brands = []
for i in q:
    brands.extend(i[1].keys())


