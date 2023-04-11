#imports
from getpass import getpass
import psycopg2
from sql_functions import create_table, add_data, get_product_ids, random_product, create_interested_products
from filters import brand_recommend, others_bought
from random import choice



#connectie maken
# Tijdelijk van getpass naar input veranderd door locale bugs
PASSWORD = input('Geef postgres wachtwoord:')
CONN = psycopg2.connect(
dbname='huwebshop',
user='postgres',
host='localhost',
password=PASSWORD
)
CURSOR = CONN.cursor()


def rec_example(cursor):
    """
    Functie voor het geven van voorbeeld van aanbevelingen

    Args:
        cursor: DBcursor
    """

    while True:
        #keuzemenu
        print("1. content filtering\n2. collaborative filtering\n3. stoppen")
        keuze = int(input("waar wil je een voorbeeld van?: "))

        #content filtering
        if keuze == 1:
            hoeveel = int(input("Hoeveel?: "))
            for i in range(hoeveel):
                product = random_product(CURSOR)
                rec_query = f"SELECT recomended_ids FROM rec_brand\nWHERE product_id = '{product}'"
                cursor.execute(rec_query)
                print(f"Meer producten van hetzelfde merk als dat van id: {product}:\nids: {cursor.fetchone()[0]}")
        
        #collaborative filtering
        elif keuze == 2:
            hoeveel = int(input("Hoeveel?: "))
            for i in range(hoeveel):
                product = random_product(CURSOR)
                cursor.execute(f"SELECT brand FROM product WHERE _id = '{product}'")
                brand = cursor.fetchone()[0]
                rec_query = f"SELECT recomended_brands FROM rec_brand_others WHERE brand = '{brand}'"
                cursor.execute(rec_query)
                print(f"Mensen die van {brand} kochten, kochten ook van merken als {cursor.fetchone()[0]}")

        #stoppen of opniew kiezen
        elif keuze == 3:
            break
        else:
            print("Kies 1, 2 of 3")


def main():
    """
    De main functie
    """
    # Tijdelijke plaatsing van deze functie
    create_interested_products(CURSOR, CONN)


    while True:
        print("1. Tables maken\n2. Data toevoegen\n3. Voorbeeld geven\n4. Sluiten")
        keuze = int(input("Keuze: "))

        if keuze == 1:
            create_table(CURSOR, CONN, "rec_brand_others", ["brand", "recomended_brands"], ["text", "text"])
            create_table(CURSOR, CONN, "rec_brand", ["product_id", "recomended_brands"], ["text", "text"])
        
        elif keuze == 2:
            ids = get_product_ids(CURSOR)
            data = brand_recommend(CURSOR)
            add_data(CURSOR, CONN, "rec_brand", data)
            data = others_bought(CURSOR, ids)
            add_data(CURSOR, CONN, "rec_brand_others", data)

        elif keuze == 3:
            rec_example(CURSOR)
        
        elif keuze == 4:
            break
        
        else:
            print("kies 1, 2, 3 of 4")


if __name__ == "__main__":
    main()

    #verbinding verbreken
    CURSOR.close()
    CONN.close()




