from random import choice
import re


def create_table(cursor, conn, table_name, columns, datatypes):
    """
    Functie voor het aanmaken van een tabel

    Args:
        cursor: DB cursor
        conn: DB connection
        table_name: String
        columns: List
        datatypes: List
    """
    #check of voor elke column een datatype is gegeven
    if len(columns) != len(datatypes):
        print("Er is niet voor elke column een datatype. Of er zijn teveel datatypes gegeven")
        return

    #maak tabel
    query = f"CREATE TABLE {table_name} (\n"

    #voeg columns toe
    for i in range(len(columns)):
        query = query + f"{columns[i]} {datatypes[i]},\n"

    query = query[:-2]
    query = query + "\n);"
    print(query)
    cursor.execute(query)
    conn.commit()


def add_data(cursor, conn, table_name, data):
    """
    Functie voor het toevoegen van data aan de database

    Args:
        cursor: DB cursor
        conn: DB connection
        table_name: String
        columns: List
        data: list
    """

    #voegt elke item in gegeven data toe aan data
    for item in data:
        query = f"INSERT INTO {table_name} VALUES {item}"
        query.replace('"', "'")
        print(query)
        cursor.execute(query)
        conn.commit()


def get_product_ids(cursor):
    """
    Functie voor het genereren van alle product_ids

    Args:
        cursor: DB cursor
    Returns:
        List of product_ids
    """

    #pak ids
    idquery = "SELECT _id\nFROM product\nWHERE brand IS NOT null"
    cursor.execute(idquery)
    ids = cursor.fetchall()

    #maak er strings van
    for id in ids:
        ids[ids.index(id)] = id[0]
    return ids


def random_product(cursor):
    """
    Functie voor het pakken van een random product id

    Args:
        cursor: DB cursor
    
    Returns:
        string
    """

    #pak ids
    query = "SELECT product_id FROM rec_brand"
    cursor.execute(query)
    ids = cursor.fetchall()

    #kies er 1
    random_id = (choice(ids))
    return random_id[0]


def create_interested_products(cursor, conn, table_name="interested_product"):
    event_table = "event"

    sql = f""" DROP TABLE IF EXISTS {table_name};

                CREATE TABLE {table_name} as SELECT b.v_id, prod.product_array AS product_array
    FROM (SELECT e1.s_id, array_agg(DISTINCT e2.product) as product_array FROM event AS e1
    LEFT JOIN {event_table} e2 ON e2.s_id = e1.s_id
    WHERE (e1.action = 'checkout' OR e1.action = 'add_to_cart')
    AND e2.product IS NOT NULL
    GROUP BY e1.s_id) prod
    INNER JOIN browserid b ON prod.s_id = b.s_id
    GROUP BY (b.v_id, prod.product_array)"""

    cursor.execute(sql)
    conn.commit()
