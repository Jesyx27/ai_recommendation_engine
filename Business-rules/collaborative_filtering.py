import psycopg2
import itertools
import json
import collections
import sql_functions

# For each profile get the profile preferences,
# Compare them to each other

# Setting up global variables about the database
DB_NAME = 'huwebshop'
USER = 'postgres'

#password = input('Fill in the password for user \'postgres\':')
password = 'postgrespassword'
# Connection to the database is established with the defined variables
conn = psycopg2.connect(f"dbname='{DB_NAME}' user='{USER}' host='localhost' password='{password}'")
cur = conn.cursor()

#                                                                           VVVVVVVVVVVVVVVVV
# Format {'native_table' : 'name', 'native_var': 'name', 'join_table': 'name ACRONYM(len = 1)', 'join_var': 'name'}
pref_inner_joins = "browserid b ON session._id = b.s_id"
pref_variables = "v_id", "preferences", "s_id"
table = "session"
weights = {'views': 1, 'sales': 6, 'add_to_carts': 3}
calc_variables = 'brand', 'category'
cond = 'preferences IS NOT NULL'
sim_variables = ('category', 'brand')


def get_sql(variables, table, inner_joins='', conditions=''):
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
    #print('SQL Done')
    return fetch


def add_data(table_name, data):
    """
    Functie voor het toevoegen van data aan de database

    Args:
        table_name: String
        data: list
    """

    per_s = ('%s,' * len(data))[:-1]

    #voegt elke item in gegeven data toe aan data
    query = f"INSERT INTO {table_name} VALUES ({per_s})"
    query.replace('"', "'")
    print(query)
    cur.execute(query, data)
    conn.commit()


def merge_preferences(variables, preferences, visitor_text, preference_text):
    """
    Merging all preferences where the user has multiple sessions

    :param variables:
    :param preferences:
    :param visitor_text:
    :param preference_text:
    :return: dict

    """

    # getting all user preferences together
    preference_dict = {}

    for i in range(len(variables)):
        if visitor_text in variables[i]:
            visitor_index = i
        elif preference_text in variables[i]:
            preferences_index = i

    for preference in preferences:

        extracted_preference = preference[preferences_index]
        visitor = preference[visitor_index]

        # If the visitor id is not yet in the dictionary with values
        if preference_dict.get(visitor) is None:
            preference_dict.update({visitor: extracted_preference})
        # If the visitor id is already in the dictionary, update the value to match
        else:
            dict_a = preference_dict.get(visitor).copy()
            dict_b = extracted_preference.copy()

            # For every key in dict_b, i.e.: brand, category, sub_category, sub_sub_category etc.
            for key_1 in dict_b:
                if type(dict_b[key_1]) == dict:
                    if key_1 not in dict_a:
                        dict_a.update({key_1: {}})
                    # For every key in dict_b[key_1], i.e: 'brandname', 'categoryname', 'sub_categoryname' etc.
                    for key_2 in dict_b[key_1]:
                        if key_2 not in dict_a[key_1]:
                            dict_a[key_1].update({key_2: {}})
                        # For every key in dict_b[key_1][key_2], i.e: views, etc.
                        for key_3 in dict_b[key_1][key_2]:
                            if key_3 not in dict_a[key_1][key_2]:
                                dict_a[key_1][key_2].update({key_3: dict_b[key_1][key_2][key_3]})
                            else:
                                dict_a[key_1][key_2].update(
                                    {key_3: dict_b[key_1][key_2][key_3] + dict_a[key_1][key_2][key_3]})

            # Update the final Dict
            preference_dict.update({visitor: dict_a})
    return preference_dict


def calculate_favorites(variables, preferences, weights):
    """
    Calculate the favorite items of visitors. with the weights

    :param variables:
    :param preferences:
    :param weights:
    :return: dict
    """

    if type(variables) != tuple and type(variables) != list:
        variables = variables,

    new_dict = {}
    recommendation = {}

    # For every v_id
    for key in preferences:
        key_dict = {}
        # For every variable, i.e.: 'brand', 'category' etc.
        for var in preferences[key]:
            if var in variables:
                var_dict = {}

                # For every variable entry, i.e: brand name ('Axe'), category type: ('Lichaamsverzorging')
                for var_entry in preferences[key][var]:
                    weight_no = 0

                    # For every property of the variable entry, i.e.: 'views', 'add_to_cart'
                    for prop in preferences[key][var][var_entry]:
                        if prop in weights.keys():
                            weight_no += preferences[key][var][var_entry][prop] * weights[prop]
                    var_dict.update({var_entry: weight_no})
                # Create a dict with the appropriate datatypes, sorted by weight
                key_dict.update({var: tuple([i[0] for i in sorted(var_dict.items(), key=lambda x:x[1])])})
        # Adding key_dict to the visitor id
        new_dict.update({key: key_dict})

    return new_dict


def get_similar_users(variables, favorites):
    if type(variables) != list and type(variables) != tuple:
        variables = variables,

    similar_dict = {}

    # For all variables
    for var in variables:
        # For all keys in the favorites
        for key_1 in favorites:
            value_1 = favorites[key_1].get(var)
            if value_1 is not None:
                recommendable_set = set()
                # For all other keys in the favorites
                for key_2 in favorites:
                    value_2 = favorites[key_2].get(var)
                    # Check if the keys are valid
                    if (value_2 is not None) and (key_1 != key_2):
                        # Compare the var (in variables) of both strings to see whether they are all the same.
                        if all([i in value_2 for i in value_1]) or all([i in value_1 for i in value_2]):
                            # Add the second key to the first.
                            recommendable_set.add(key_2)
                # If the current user is not yet in the dictionary.
                if similar_dict.get(key_1) is None:
                    similar_dict.update({key_1: recommendable_set})
                # If not, add it to the current.
                else:
                    similar_dict[key_1] = similar_dict[key_1].union(set(recommendable_set))

    return similar_dict


def get_recommendables(similar_users):
    """
    Get the recommendable items from the similar users by getting the recommendations they viewed before.

    :param similar_users:
    :return: dict
    """

    recommendable_dict = {}

    variables = 'recommendations_viewed_before'

    # For each user in the similar user set.
    for user in similar_users:
        products = set()

        # If the user has any similar users
        if len(similar_users[user]) > 0:
            # Setting up the recommendable dictionary
            conditions = f'_id in {tuple(similar_users[user])}'
            x = [set(i[0]) for i in (get_sql(variables=variables, table='visitor', conditions=conditions))]
            for i in x:
                # Update de products set
                products.update(i)
        if len(products) > 0:
            recommendable_dict.update({user: tuple(products)})

    return recommendable_dict


def regular_call():
    """
    This is the regular way this module is to be run, it executes the collaborative filtering without
    :return:
        The output from the collaborative filtering
    """

    preferences_variables = get_sql(variables=pref_variables, inner_joins=pref_inner_joins, table=table,
                                    conditions=cond)

    mp = merge_preferences(preferences=preferences_variables,
                           variables=pref_variables,
                           visitor_text='v_id',
                           preference_text="preferences")

    favorite = calculate_favorites(variables=calc_variables, preferences=mp, weights=weights)
    sim = get_similar_users(variables=sim_variables, favorites=favorite)
    return get_recommendables(sim)


if __name__ == '__main__':
    table_name = 'collaborative_a'
    a = regular_call()
    sql_functions.create_table(cur, conn, table_name, ('v_id', 'products'), ('text', 'text[]'))

    for i in a:
        if len(a[i]) > 0:
            add_data(table_name, (i, list(a[i])))
            #print(i, a[i])
