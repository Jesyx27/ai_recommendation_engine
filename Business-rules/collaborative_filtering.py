

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