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

def get_all_appliance(user_id):
    base_path = Path(__file__).parent
    file_path = (base_path / "../databases/userdata.json").resolve()

    with open(file_path, 'r') as f:
        db_data = json.load(f)

        for item in db_data:
            if item['chat_id'] == user_id:
                return item['appliances']
