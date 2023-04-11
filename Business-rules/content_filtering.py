def discount_recommend(conn, cursor):
    """
    Functie voor het recommenderen van producten met een aanbieding

    Args:
        conn: DB connection
        cursor: DB cursor
    """

    query = "SELECT *\nFROM product\nWHERE price_discount IS NOT NULL\nORDER BY price_discount DESC"

    cursor.execute(query)
    return cursor.fetchall()
