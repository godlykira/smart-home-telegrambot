import json
from pathlib import Path

def create_user_db(chat_id):
    """
    Create a user database and add a new user with the given chat_id. 
    This function takes the chat_id as a parameter and does not return anything.
    """
    base_path = Path(__file__).parent
    file_path = (base_path / "../databases/userdata.json").resolve()

    with open(file_path, 'r') as f:
        data = json.load(f)

        temp_dist = {
            "chat_id": chat_id,
            "appliances": [],
            "password": None,
            "card": None
        }

        data.append(temp_dist)

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

def add_to_temp(chat_id, data):
    """
    Function to add data to a temporary file.

    Parameters:
    chat_id (int): The ID of the chat.
    data (str): The data to be added to the file.
    """
    base_path = Path(__file__).parent
    file_path = (base_path / f"../temp/{chat_id}.txt").resolve()

    with open(file_path, 'a') as f:
        f.write(data + '\n')

def add_appliance(chat_id):
    """
    Adds an appliance for the given chat ID. Reads the appliance data from a text file based on the chat ID, and adds it to the user data stored in a JSON file. Removes the temporary appliance file after updating the user data.
    Parameters:
    - chat_id: The ID of the chat for which the appliance is being added.
    """
    base_path = Path(__file__).parent
    file_path1 = (base_path / f"../temp/{chat_id}.txt").resolve()
    file_path2 = (base_path / "../databases/userdata.json").resolve()

    with open(file_path1, 'r') as f:
        data = f.readlines()

        appliance = {
            "name": data[1].strip(),
            "category": data[0].strip(),
            "status": False
        }

        with open(file_path2, 'r') as f:
            db_data = json.load(f)

            for item in db_data:
                if item['chat_id'] == chat_id:
                    item['appliances'].append(appliance)

                    with open(file_path2, 'w') as f:
                        json.dump(db_data, f, indent=2)
        
    file_path1.unlink()
  
def remove_appliance(chat_id, appliance_index):
    base_path = Path(__file__).parent
    file_path = (base_path / "../databases/userdata.json").resolve()

    with open(file_path, 'r') as f:
        db_data = json.load(f)

        for item in db_data:
            if item['chat_id'] == chat_id:
                item['appliances'].pop(int(appliance_index) - 1)

                with open(file_path, 'w') as f:
                    json.dump(db_data, f, indent=2)

def update_appliance_status(chat_id, appliance_index):
    base_path = Path(__file__).parent
    file_path = (base_path / "../databases/userdata.json").resolve()

    with open(file_path, 'r') as f:
        db_data = json.load(f)

        for item in db_data:
            if item['chat_id'] == chat_id:
                item['appliances'][int(appliance_index) - 1]['status'] = True if item['appliances'][int(appliance_index) - 1]['status'] is False else False

                with open(file_path, 'w') as f:
                    json.dump(db_data, f, indent=2)

def get_categories():
    """
    Retrieve categories from the appliancedata.json file and return a dictionary with categories and the full database data.
    """
    base_path = Path(__file__).parent
    file_path = (base_path / "../databases/appliancedata.json").resolve()

    with open(file_path, 'r') as f:
        db_data = json.load(f)

        only_categories = [[x for x in db_data.keys()]]
        return {'categories': only_categories, 'data': db_data}

def get_all_appliance(chat_id):
    """
    Retrieves all appliances associated with the given user ID from the database.
    
    Args:
        chat_id (str): The ID of the chat to retrieve appliances for.
    
    Returns:
        list: A list of appliances associated with the given user ID.
    """
    base_path = Path(__file__).parent
    file_path = (base_path / "../databases/userdata.json").resolve()

    with open(file_path, 'r') as f:
        db_data = json.load(f)

        for item in db_data:
            if item['chat_id'] == chat_id:
                return item['appliances']

def user_total_usage(chat_id):
    """
    Calculate the total usage of all appliances for a given user.

    Args:
        chat_id (int): The id of the chat to calculate the total usage for.

    Returns:
        int: The total usage of all appliances for the given user.
    """
    base_path = Path(__file__).parent
    file_path1 = (base_path / "../databases/userdata.json").resolve()
    file_path2 = (base_path / "../databases/appliancedata.json").resolve()

    with open(file_path1, 'r') as f:
        with open(file_path2, 'r') as f2:
            db_data1 = json.load(f)
            db_data2 = json.load(f2)

            for item in db_data1:
                if item['chat_id'] == chat_id:
                    total = 0
                    for x in item['appliances']:
                        if x['status'] is True:
                            print(db_data2[x['category']], x['status'])
                            total += db_data2[x['category']]
                    return total
                
def get_current(category):
    """
    Retrieves the data for the given category from the appliancedata.json file.

    Args:
        category: A string representing the category for which to retrieve the data.

    Returns:
        The data corresponding to the given category from the appliancedata.json file.
    """
    base_path = Path(__file__).parent
    file_path = (base_path / "../databases/appliancedata.json").resolve()

    with open(file_path, 'r') as f:
        db_data = json.load(f)

        return db_data[category]

def add_passkey(chat_id, passkey):
    """
    Updates the passkey for the specified user in the user data JSON file.

    Args:
        chat_id (int): The ID of the user for which the passkey is being updated.
        passkey (str): The new passkey for the user.

    Returns:
        None
    """
    base_path = Path(__file__).parent
    file_path = (base_path / "../databases/userdata.json").resolve()

    with open(file_path, 'r') as f:
        db_data = json.load(f)

        for item in db_data:
            if item['chat_id'] == chat_id:
                item['password'] = passkey

                with open(file_path, 'w') as f:
                    json.dump(db_data, f, indent=2)

def add_keycard(chat_id, keycard):
    base_path = Path(__file__).parent
    file_path = (base_path / "../databases/userdata.json").resolve()

    with open(file_path, 'r') as f:
        db_data = json.load(f)

        for item in db_data:
            if item['chat_id'] == chat_id:
                item['card'] = keycard

                with open(file_path, 'w') as f:
                    json.dump(db_data, f, indent=2)