import os, re, uuid
from flask import session
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL   # import the function that will return an instance of a connection


# Get the current file's directory.
current_directory = os.path.dirname(__file__)



# //////////////////////////////////////////////  Locations Validations  //////////////////////////////////////////////
# ///////////////////////////////////////////////// ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ ////////////////////////////////////////////////


# Validations for the add_new_location method.
def validate_add_new_location_method(form_data, form_files):
    validation_errors = []
    data = {
        'location_id_from_form': form_data['location_id'],
        'location_name_from_form': form_data['location_name'],
        'creation_user_id': form_data['user_id']
    }

    # Validate location_id length.
    if len(data['location_id_from_form']) < 5 or len(data['location_id_from_form']) > 20:
        validation_errors.append("Location ID must be between 5 and 20 characters in length.")
    else:
        # Check if location_id already exists in the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        query = "SELECT COUNT(*) AS count FROM locations WHERE location_id = %(location_id_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0:
            validation_errors.append("A location with the same ID already exists.")

    # Validate location's name length.
    if len(data['location_name_from_form']) < 5 or len(data['location_name_from_form']) > 20:
        validation_errors.append("Location name must be between 5 and 20 characters in length.")
    else:
        # Check if location's name already exists in the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        query = "SELECT COUNT(*) AS count FROM locations WHERE name = %(location_name_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0:
            validation_errors.append("A location with the same name already exists.")

    # Validate location's image:
    # If the user decided to uplaod a photo file:
    media_file = None
    if "location_image" in form_files and form_files['location_image'].filename != '':
        media_file = form_files['location_image']
        media_type = media_file.content_type.split('/')
        if not validate_type_of_uploaded_media_file(media_type, { 'image': ('apng', 'bmp', 'gif', 'jpeg', 'jpg', 'png', 'webp', 'svg') }):
            validation_errors.append("An uploaded file type is not image!")
            return data, validation_errors

        # Define the relative path to the target directory.
        relative_path = 'static/uploads/locations_photos'
        # Construct the complete path to save the image.
        image_path = os.path.join(current_directory, '..', relative_path)
        # Process the uploaded image.
        original_filename = secure_filename(media_file.filename)
        # Generate a unique filename (image_id) using UUID.
        image_id = f"{uuid.uuid4()}_{original_filename}"
        # Append the image_id to the path.
        image_path = os.path.join(image_path, image_id)
        # Save the file.
        media_file.save(image_path)

        # Validate size of media file.
        if not validate_size_of_uploaded_media_file(image_path, media_type[0]):
            validation_errors.append("An uploaded image file size is above the maximum which is 25MB.")
            # Remove the media file from the server.
            os.remove(image_path)
            return data, validation_errors

    # Validate location's image:
    elif 'location_image' not in form_files or form_files['location_image'].filename == '':  
        image_id = "default_location.png"

    data['location_image_from_form'] = image_id
    return data, validation_errors



# Validations for the update_location method.
def validate_update_location_method(form_data, form_files):
    validation_errors = []
    data = {
        'location_id_from_form': form_data['location_id'],
        'old_location_id_from_form': form_data['old_location_id'],
        'location_name_from_form': form_data['location_name'],
        'old_location_name_from_form': form_data['old_location_name'],
        'updation_user_id': form_data['user_id'],
        'old_image_from_form': form_data['old_image']
    }

    # Validate location_id length.
    if len(data['location_id_from_form']) < 5 or len(data['location_id_from_form']) > 20:
        validation_errors.append("Location ID must be between 5 and 20 characters in length.")
    else:
        # Check if location_id already exists in the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        query = "SELECT COUNT(*) AS count FROM locations WHERE location_id = %(location_id_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0 and data['location_id_from_form'] != data['old_location_id_from_form']:
            validation_errors.append("A location with the same ID already exists.")

    # Validate location's name length.
    if len(data['location_name_from_form']) < 5 or len(data['location_name_from_form']) > 20:
        validation_errors.append("Location name must be between 5 and 20 characters in length.")
    else:
        # Check if location's name already exists in the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        query = "SELECT COUNT(*) AS count FROM locations WHERE name = %(location_name_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0 and data['location_name_from_form'] != data['old_location_name_from_form']:
            validation_errors.append("A location with the same name already exists.")

    # Validate location's image:
    # If the user decided to uplaod a new photo file:
    media_file = None
    if "location_image" in form_files and form_files['location_image'].filename != '':
        media_file = form_files['location_image']
        media_type = media_file.content_type.split('/')
        if not validate_type_of_uploaded_media_file(media_type, { 'image': ('apng', 'bmp', 'gif', 'jpeg', 'jpg', 'png', 'webp', 'svg') }):
            validation_errors.append("An uploaded file type is not image!")
            return data, validation_errors

        # Define the relative path to the target directory (one level up).
        relative_path = 'static/uploads/locations_photos'

        # Construct the complete path to save the image.
        image_path = os.path.join(current_directory, '..', relative_path)
        # Process the uploaded image.
        file = form_files['location_image']
        original_filename = secure_filename(media_file.filename)
        # Generate a unique filename (image_id) using UUID.
        image_id = f"{uuid.uuid4()}_{original_filename}"
        # Append the image_id to the path.
        image_path = os.path.join(image_path, image_id)
        # Save the file.
        media_file.save(image_path)

        # Validate size of media file.
        if not validate_size_of_uploaded_media_file(image_path, media_type[0]):
            validation_errors.append("An uploaded image file size is above the maximum which is 25MB.")
            # Remove the media file from the server.
            os.remove(image_path)
            return data, validation_errors

        # Construct the path to the old image to replace it with the new one.
        # (You can remove the next 5 lines if u want to keep the old image along with the new one)
        old_image_path = os.path.join(current_directory, '..', relative_path, form_data['old_image'])
        # Check if the old image file exists and it's not the default image before trying to delete it
        if os.path.exists(old_image_path) and form_data['old_image'] != 'default_location.png':
            # Delete the old image file
            os.remove(old_image_path)

    # Validate location's image if the user didnt update it, then use the old one:
    elif 'location_image' not in form_files:
        image_id =  data['old_image_from_form']

    data['location_image_from_form'] = image_id
    return data, validation_errors




# //////////////////////////////////////////////  Products Validations  //////////////////////////////////////////////
# //////////////////////////////////////////////// ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ ////////////////////////////////////////////////


# Validations for the add_new_product method.
def validate_add_new_product_method(form_data):
    validation_errors = []
    first_sec_validation = None

    # If the first checkbox is checked (add existing product).
    if 'new_product_checkbox' not in form_data:
        first_sec_validation = True
        data = {
            'product_quantity_1_from_form' : form_data['product_quantity_1'],
            'movement_id_1_from_form' : form_data['movement_id_1'],
            'creation_user_id': form_data['user_id']
        }

        # Validate product_id when the user doesn't select any neither from the select menu nor typing down an ID in the text input.
        if 'product_id_select_1' in form_data and 'product_id_input_1' in form_data:
            validation_errors.append("You must choose a product either from the select menu or type its ID directly in the text area.")
        # If the user entered a product_id manually in the text input.
        elif 'product_id_input_1' in form_data:
            data['product_id_from_form'] = form_data['product_id_input_1']
            # Check if product_id exists in the database.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            query = "SELECT COUNT(*) AS count FROM products WHERE  product_id = %(product_id_from_form)s" 
            result = mysql.query_db(query, data)
            # If entered product_id didn't match any product ID in the database.
            if result[0]['count'] == 0:
                validation_errors.append("No product ID matched the entered one, please try again with valid ID.")
        # If the user chosed a product_id from the select menu.
        elif 'product_id_select_1' in form_data:
            data['product_id_from_form'] = form_data['product_id_select_1']

        # Validate the quantity of the product if the user left it blank or not.
        if data['product_quantity_1_from_form'] == "":
            validation_errors.append("Please insert a number in the quantity area.")
        else:
            movement_quantity = float(data['product_quantity_1_from_form'])
            # Validate the quantity if it's less than or equal to zero or has decimal values.
            if movement_quantity <= 0 or not movement_quantity.is_integer():
                validation_errors.append("Please insert a positive integer number as the quantity.")

        # Validate movement_id length.
        if len(data['movement_id_1_from_form']) < 5 or len(data['movement_id_1_from_form']) > 20:
            validation_errors.append("Movement ID must be between 5 and 20 characters in length.")
        else:
            # Check if movement_id already exists in the database.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            query = "SELECT COUNT(*) AS count FROM movements WHERE movement_id = %(movement_id_1_from_form)s"
            result = mysql.query_db(query, data)
            if result[0]['count'] > 0:
                validation_errors.append("A movement with the same ID already exists.")

        # Validate from_location_id is present and selected by the user.
        if 'product_location_id_1' not in form_data or form_data['product_location_id_1'] == "":
            validation_errors.append("You must select a Location.")
        else:
            data["product_to_location_id_1_from_form"] = form_data['product_location_id_1']

    # If the second checkbox is checked (add new product).
    else:
        first_sec_validation = False
        data = {
            'product_id_2_from_form' : form_data['product_id_2'],
            'product_name_2_from_form' : form_data['product_name_2'],
            'product_price_2_from_form' : form_data['product_price_2'],
            'product_quantity_2_from_form' : form_data['product_quantity_2'],
            'movement_id_2_from_form' : form_data['movement_id_2'],
            'creation_user_id': form_data['user_id']
        }

        # Validate product_id length.
        if len(data['product_id_2_from_form']) < 5 or len(data['product_id_2_from_form']) > 20:
            validation_errors.append("Product ID must be between 5 and 20 characters in length.")
        else:
            # Check if product_id already exists in the database.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            query = "SELECT COUNT(*) AS count FROM products WHERE product_id = %(product_id_2_from_form)s"
            result = mysql.query_db(query, data)
            if result[0]['count'] > 0:
                validation_errors.append("A product with the same ID already exists.")
        
        # Validate product's name length.
        if len(data['product_name_2_from_form']) < 3 or len(data['product_name_2_from_form']) > 20:
            validation_errors.append("Product name must be between 3 and 20 characters in length.")
        else:
            # Check if product's name already exists in the database.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            query = "SELECT COUNT(*) AS count FROM products WHERE  name = %(product_name_2_from_form)s"
            result = mysql.query_db(query, data)
            if result[0]['count'] > 0:
                validation_errors.append("A product with the same name already exists.")

        # Validate product's price.'
        if data['product_price_2_from_form'] == "":
            validation_errors.append("Please insert a price for the product.")
        elif float(data['product_price_2_from_form']) <= 0:
            validation_errors.append("Please insert a positive number as a price.")

        # Validate the quantity of the product if the user left it blank or not.
        if data['product_quantity_2_from_form'] == "":
            validation_errors.append("Please insert a number in the quantity area.")
        else:
            movement_quantity = float(data['product_quantity_2_from_form'])
            # Validate the quantity if it's less than or equal to zero or has decimal values.
            if movement_quantity <= 0 or not movement_quantity.is_integer():
                validation_errors.append("Please insert a positive integer number as the quantity.")

        # Validate movement_id length.
        if len(data['movement_id_2_from_form']) < 5 or len(data['movement_id_2_from_form']) > 20:
            validation_errors.append("Movement ID must be between 5 and 20 characters in length.")
        else:
            # Check if movement_id already exists in the database.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            query = "SELECT COUNT(*) AS count FROM movements WHERE movement_id = %(movement_id_2_from_form)s"
            result = mysql.query_db(query, data)
            if result[0]['count'] > 0:
                validation_errors.append("A movement with the same ID already exists.")

        # Validate location_id is present and selected by the user.
        if 'product_location_id_2' not in form_data or form_data['product_location_id_2'] == "":
            validation_errors.append("You must select a Location.")
        else:
            data["product_to_location_id_2_from_form"] = form_data['product_location_id_2']

    return data, validation_errors, first_sec_validation



# Validations for the update_product method.
def validate_update_product_method(form_data):
    validation_errors = []
    data = {
        'product_id_from_form': form_data['product_id'],
        'old_product_id_from_form': form_data['old_product_id'],
        'product_name_from_form': form_data['product_name'],
        'old_product_name_from_form': form_data['old_product_name'],
        'product_price_from_form': form_data['product_price'],
        'updation_user_id': form_data['user_id']
    }

    # Validate product_id length.
    if len(data['product_id_from_form']) < 5 or len(data['product_id_from_form']) > 20:
        validation_errors.append("Product ID must be between 5 and 20 characters in length.")
    else:
        # Check if product_id already exists in the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        query = "SELECT COUNT(*) AS count FROM products WHERE  product_id = %(product_id_from_form)s" 
        result = mysql.query_db(query, data)
        # If the user didn't cahnge the ID:
        if result[0]['count'] > 0 and data['product_id_from_form'] != data['old_product_id_from_form']:
            validation_errors.append("A product with the same ID already exists.")

    # Validate product's name length.
    if len(data['product_name_from_form']) < 3 or len(data['product_name_from_form']) > 20:
        validation_errors.append("Product name must be between 3 and 20 characters in length.")
    else:
        # Check if product's name already exists in the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        query = "SELECT COUNT(*) AS count FROM products WHERE  name = %(product_name_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0 and data['product_name_from_form'] != data['old_product_name_from_form']:
            validation_errors.append("A product with the same name already exists.")

    # Validate product's price.'
    if data['product_price_from_form'] == "":
        validation_errors.append("Please insert a price for the product.")
    elif float(data['product_price_from_form']) <= 0:
        validation_errors.append("Please insert a positive number as a price.")

    return data, validation_errors




# //////////////////////////////////////////////  Movements Validations  ///////////////////////////////////////////////
# //////////////////////////////////////////////// ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ /////////////////////////////////////////////////


# Validations for the add_new_movement method.
def validate_add_new_movement_method(form_data):
    validation_errors = []

    data = {
        'movement_id_from_form': form_data['movement_id'],
        'movement_quantity_from_form': form_data['movement_quantity'],
        'creation_user_id': form_data['user_id']
    }

    # Validate movement_id length.
    if len(data['movement_id_from_form']) < 5 or len(data['movement_id_from_form']) > 20:
        validation_errors.append("Movement ID must be between 5 and 20 characters in length.")
    else:
        # Check if movement_id already exists in the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        query = "SELECT COUNT(*) AS count FROM movements WHERE movement_id = %(movement_id_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0:
            validation_errors.append("A movement with the same ID already exists.")

    # Validate from_location_id is present and selected by the user.
    if 'from_location_id' not in form_data:
        validation_errors.append("You must select a 'From Location' first!")
    else:
        data["from_location_id_from_form"] = form_data['from_location_id']
        data["to_location_id_from_form"] = form_data['to_location_id']

        # Validate product_id when the user doesn't select any neither from the select menu nor typing down an ID in the text input.
        if 'product_id_input'in form_data and 'product_id_select' in form_data:
            validation_errors.append("You must choose a product either from the select menu or type its ID directly in the text area.")
        else:
            # Validate product_id when the user used the select input to choose a product.
            if 'product_id_select' in form_data and 'product_id_input' not in form_data:
                data['product_id_from_form'] = form_data['product_id_select']
            # Validate product_id when the user used the text input to enter a product id manually if he chosed any location rather "Out Sourcing" as a "From Location".
            elif form_data['product_id_input'] != "" and form_data['from_location_id'] != "out":
                # Validate product_id length.
                if len(form_data['product_id_input']) < 5 or len(form_data['product_id_input']) > 20:
                    validation_errors.append("Product ID must be between 5 and 20 characters in length.")
                    return data, validation_errors
                # Validate product_id availability in from_location when the user writes the product ID (product quantity in location > 0).
                data['product_id_from_form'] = form_data['product_id_input']
                mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
                query = """
                    SELECT 
                        COALESCE(SUM(CASE WHEN m.to_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) -
                        COALESCE(SUM(CASE WHEN m.from_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) AS total_quantity
                    FROM movements m
                    WHERE m.product_id = %(product_id_from_form)s
                """
                result = mysql.query_db(query, data)
                total_quantity = result[0]['total_quantity']
                if total_quantity < 1:
                    validation_errors.append("The selected product is not available in the 'from' location.")
                    return data, validation_errors
            # Validate product_id when the user used the text input to enter a product id manually if he chosed "Out Sourcing" as a "From Location".
            elif form_data['product_id_input'] != "" and form_data['from_location_id'] == "out":
                # Validate product_id length.
                if len(form_data['product_id_input']) < 5 or len(form_data['product_id_input']) > 20:
                    validation_errors.append("Product ID must be between 5 and 20 characters in length.")
                    return data, validation_errors
                # Validate product_id is available in all products.
                data['product_id_from_form'] = form_data['product_id_input']
                mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
                query = """
                    SELECT COUNT(*) AS product_count FROM products WHERE product_id = %(product_id_from_form)s
                """
                result = mysql.query_db(query, data)
                matched_products = result[0]['product_count']
                if matched_products == 0:
                    validation_errors.append("The selected product ID is not available.")
                    return data, validation_errors

            # Validate the quantity of the movement if the user left it blank or not.
            if data['movement_quantity_from_form'] == "":
                validation_errors.append("Please insert a number in the quantity area.")
            else:
                movement_quantity = float(data['movement_quantity_from_form'])
                # Validate the quantity if it's less than or equal to zero or has decimal values.
                if movement_quantity <= 0 or not movement_quantity.is_integer():
                    validation_errors.append("Please insert a positive integer number as the quantity.")
                else:
                    if form_data['from_location_id'] != "out":
                        # Validate product_id availability in from_location (if the quantity in the location is more than or equal to movement's quantity).
                        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
                        query = """
                            SELECT 
                                COALESCE(SUM(CASE WHEN m.to_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) -
                                COALESCE(SUM(CASE WHEN m.from_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) AS total_quantity
                            FROM movements m
                            WHERE m.product_id = %(product_id_from_form)s
                        """
                        result = mysql.query_db(query, data)
                        total_quantity = result[0]['total_quantity']
                        if total_quantity < int(movement_quantity):
                            validation_errors.append("The selected quantity is more than the available quantity.")

    return data, validation_errors



# Validations for the update_movement method.
def validate_update_movement_method(form_data):
    validation_errors = []

    data = {
        'movement_id_from_form': form_data['movement_id'],
        'old_movement_id_from_form': form_data['old_movement_id'],
        'movement_quantity_from_form': form_data['movement_quantity'],
        'from_location_id_from_form': form_data['from_location_id'],
        'to_location_id_from_form': form_data['to_location_id'],
        'old_from_location_id': form_data['old_from_location_id'],
        'old_to_location_id': form_data['old_to_location_id'],
        'old_product_id': form_data['old_product_id'],
        'old_movement_quantity': form_data['old_movement_quantity'],
        'updation_user_id': form_data['user_id']
    }

    # Validate movement_id length.
    if len(data['movement_id_from_form']) < 5 or len(data['movement_id_from_form']) > 20:
        validation_errors.append("Movement ID must be between 5 and 20 characters in length.")
    else:
        # Check if movement_id already exists in the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        query = "SELECT COUNT(*) AS count FROM movements WHERE movement_id = %(movement_id_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0 and data['movement_id_from_form'] != data['old_movement_id_from_form']:
            validation_errors.append("A movement with the same ID already exists.")

    # If the user used the select menu to choose a product.
    if 'product_id_select' in form_data and 'product_id_input' not in form_data:
        data['product_id_from_form'] = form_data['product_id_select']

        # If "From Location" is "Out Sourcing".
        if data['from_location_id_from_form'] == "out":
            # Validate the quantity of the movement if the user left it blank or not.
            if data['movement_quantity_from_form'] == "":
                validation_errors.append("Please insert a number in the quantity area.")
            else:
                movement_quantity = float(data['movement_quantity_from_form'])
                # Validate the quantity if it's less than or equal to zero or has decimal values.
                if movement_quantity <= 0 or not movement_quantity.is_integer():
                    validation_errors.append("Please insert a positive integer number as the quantity.")
            return data, validation_errors

        else:
            # Validate the quantity of the movement if the user left it blank or not.
            if data['movement_quantity_from_form'] == "":
                validation_errors.append("Please insert a number in the quantity area.")
            else:
                movement_quantity = float(data['movement_quantity_from_form'])
                # Validate the quantity if it's less than or equal to zero or has decimal values.
                if movement_quantity <= 0 or not movement_quantity.is_integer():
                    validation_errors.append("Please insert a positive integer number as the quantity.")
                else:
                    # Validate product_id availability in from_location (if the quantity in the location is more than or equal to movement's quantity).
                    mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
                    query = """
                        SELECT 
                            COALESCE(SUM(CASE WHEN m.to_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) -
                            COALESCE(SUM(CASE WHEN m.from_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) AS total_quantity
                        FROM movements m
                        WHERE m.product_id = %(product_id_from_form)s
                    """
                    result = mysql.query_db(query, data)
                    total_quantity = result[0]['total_quantity']
                    # If the product also didn't change.
                    if data['product_id_from_form'] == data['old_product_id']:
                        if (data['from_location_id_from_form'] == data['old_from_location_id']) and (data['product_id_from_form'] == data['old_product_id']) :
                            total_quantity = total_quantity + int(data["old_movement_quantity"])
                        elif(data['from_location_id_from_form'] == data['old_to_location_id']) and (data['product_id_from_form'] == data['old_product_id']) :
                            total_quantity = total_quantity - int(data["old_movement_quantity"])
                    if total_quantity <= 0:
                        validation_errors.append("The selected product is not available in the 'from' location.")
                    elif movement_quantity > total_quantity:
                        validation_errors.append("The selected quantity is more than the available quantity.")
            return data, validation_errors

    # If the user used the text input choose a product.
    # Validate product_id availability in from_location when the user writes the product ID (product quantity in location > 0).
    elif ('product_id_input' in form_data and 'product_id_select' not in form_data) or (form_data['product_id_input'] != "" and form_data['product_id_select'] == ""):
        # If the length of the ID is not enough (less than 5 chracters).
        if len(form_data['product_id_input']) < 5 or len(form_data['product_id_input']) > 20:
            validation_errors.append("Product ID must be between 5 and 20 characters in length.")
            return data, validation_errors

        data['product_id_from_form'] = form_data['product_id_input']
        # If "From Location" is "Out Sourcing".
        if data['from_location_id_from_form'] == "out":
            # Validate product_id when the user used the text input to enter a product id manually if he chosed None as a "From Location".
            # Validate product_id is available in "all products".
            data['product_id_from_form'] = form_data['product_id_input']
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            query = """
                SELECT COUNT(*) AS product_count FROM products WHERE product_id = %(product_id_from_form)s
            """
            result = mysql.query_db(query, data)
            matched_products = result[0]['product_count']
            if matched_products == 0:
                validation_errors.append("The selected product ID is not available.")
            # Validate the quantity of the movement if the user left it blank or not.
            elif data['movement_quantity_from_form'] == "":
                validation_errors.append("Please insert a number in the quantity area.")
            else:
                movement_quantity = float(data['movement_quantity_from_form'])
                # Validate the quantity if it's less than or equal to zero or has decimal values.
                if movement_quantity <= 0 or not movement_quantity.is_integer():
                    validation_errors.append("Please insert a positive integer number as the quantity.")
            return data, validation_errors

        else:
            # Validate product_id availability in from_location (if the quantity in the location is more than or equal to movement's quantity).
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            query = """
                SELECT 
                    COALESCE(SUM(CASE WHEN m.to_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN m.from_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) AS total_quantity
                FROM movements m
                WHERE m.product_id = %(product_id_from_form)s
            """
            result = mysql.query_db(query, data)
            total_quantity = result[0]['total_quantity']

            # If the product also didn't change.
            if data['product_id_from_form'] == data['old_product_id']:
                if (data['from_location_id_from_form'] == data['old_from_location_id']) and (data['product_id_from_form'] == data['old_product_id']) :
                    total_quantity = total_quantity + int(data["old_movement_quantity"])

                elif(data['from_location_id_from_form'] == data['old_to_location_id']) and (data['product_id_from_form'] == data['old_product_id']) :
                    total_quantity = total_quantity - int(data["old_movement_quantity"])
            if total_quantity <= 0:
                validation_errors.append("The selected product is not available in the 'from' location.")
            # Validate the quantity of the movement if the user left it blank or not.
            elif data['movement_quantity_from_form'] == "":
                validation_errors.append("Please insert a number in the quantity area.")
            else:
                movement_quantity = float(data['movement_quantity_from_form'])
                # Validate the quantity if it's less than or equal to zero or has decimal values.
                if movement_quantity <= 0 or not movement_quantity.is_integer():
                    validation_errors.append("Please insert a positive integer number as the quantity.")
                if movement_quantity > total_quantity:
                    validation_errors.append("The selected quantity is more than the available quantity.")
            return data, validation_errors

    # If the user didn't choose any product ID neither from the select noe from the text input.
    elif form_data['product_id_input'] == "" and form_data['product_id_select'] == "":
        validation_errors.append("You must select a product or enter valid product ID.")
        return data, validation_errors




# /////////////////////////////////////////////////  Users Validations  ////////////////////////////////////////////////
# //////////////////////////////////////////////// ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ /////////////////////////////////////////////////


# Validations for the update_user_profile method.
def validate_update_user_profile_method(form_data, form_files, checked_user):
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
    NAME_REGEX = re.compile(r"^[a-zA-Z ,.'-]+$")
    validation_errors = []

    data = {
        'first_name_from_form': form_data['first_name'],         
        'last_name_from_form': form_data['last_name'],
        'email_from_form': form_data['email'],
        'gender_from_form': form_data['gender'],
        'phone_from_form': form_data['phone'],
        'job_title_from_form': form_data['job_title'],
        'country_from_form': form_data['country'],
        'city_from_form': form_data['city'],
        'street_from_form': form_data['street'],
        'postal_code_from_form': form_data['postal_code'],
        'user_id_from_session': session['user_id'],
        'old_email_form_form': form_data['old_email']
    }

    # First Name:
    if len(form_data['first_name']) < 2:
        validation_errors.append(("First Name must be at least 2 characters.", 'first_name'))
    elif not NAME_REGEX.match(form_data['first_name']):
        validation_errors.append(("First Name field can not contain numbers or unusual signs.", 'first_name'))
    if len(form_data['first_name']) > 50:
        validation_errors.append(("First Name must be at most 50 characters.", 'first_name'))

    # Last Name:
    if len(form_data['last_name']) < 2:
        validation_errors.append(("Last Name must be at least 2 characters.", 'last_name'))
    elif not NAME_REGEX.match(form_data['last_name']):
        validation_errors.append(("Last Name field can not contain numbers or unusual signs.", 'last_name'))
    if len(form_data['last_name']) > 50:
        validation_errors.append(("Last Name must be at most 50 characters.", 'last_name'))

    # Email:
    if len(form_data['email']) < 1:
        validation_errors.append(("Please, enter your email.", 'email'))
    elif not EMAIL_REGEX.match(form_data['email']):
        validation_errors.append(("Invalid email address.", 'email'))
    # Check if the entered email already used before.
    mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
    emails_query = "SELECT COUNT(*) AS count FROM users WHERE email = %(email_from_form)s;"
    result = mysql.query_db(emails_query, data)
    if result[0]['count'] > 0 and data['email_from_form'] != data['old_email_form_form']:
        validation_errors.append("A location with the same ID already exists.", 'email')

    # Gender:
    if ('gender' not in form_data) or (form_data['gender'] == ""):
        validation_errors.append(("Please select your gender.", 'gender'))

    # Phone Number:
    if ('phone' not in form_data) or (form_data['phone'] == ""):
        validation_errors.append(("Please enter your phone number.", 'phone'))

    # Job Title.
    if ('job_title' not in form_data) or (form_data['job_title'] == ""):
        validation_errors.append(("Please select your job title.", 'job_title'))

    # Country:
    if ('country' not in form_data) or (form_data['country'] == ""):
        validation_errors.append(("Please select your country.", 'country'))

    # City:
    if len(form_data['city']) < 2:
        validation_errors.append(("City name must be at least 2 characters.", 'city'))
    elif len(form_data['city']) > 50:
        validation_errors.append(("City name must be at most 50 characters.", 'city'))

    # Street:
    if len(form_data['street']) < 2:
        validation_errors.append(("Street name must be at least 2 characters.", 'street'))
    elif len(form_data['street']) > 50:
        validation_errors.append(("Street name must be at most 50 characters.", 'street'))

    # Postal Code:
    if len(form_data['postal_code']) < 1:
        validation_errors.append(("Please enter your postal code.", 'postal_code'))
    elif len(form_data['postal_code']) > 10:
        validation_errors.append(("Postal code can't be more than 10 characters.", 'postal_code'))

    # Validate user's image:
    # If the user decided to uplaod a new photo file:
    media_file = None
    if "user_image" in form_files and form_files['user_image'].filename != '':
        media_file = form_files['user_image']
        media_type = media_file.content_type.split('/')
        if not validate_type_of_uploaded_media_file(media_type, { 'image': ('apng', 'bmp', 'gif', 'jpeg', 'jpg', 'png', 'webp', 'svg') }):
            validation_errors.append("An uploaded file type is not image!")
            return data, validation_errors

        # Define the relative path to the target directory (one level up).
        relative_path = 'static/uploads/users_photos'

        # Construct the complete path to save the image.
        image_path = os.path.join(current_directory, '..', relative_path)
        # Process the uploaded image.
        original_filename = secure_filename(media_file.filename)
        # Generate a unique filename (image_id) using UUID.
        image_id = f"{uuid.uuid4()}_{original_filename}"
        # Append the image_id to the path.
        image_path = os.path.join(image_path, image_id)
        # Save the file.
        media_file.save(image_path)

        # Validate size of media file.
        if not validate_size_of_uploaded_media_file(image_path, media_type[0]):
                validation_errors.append("An uploaded image file size is above the maximum which is 25MB.")
                return data, validation_errors

        # Construct the path to the old image to replace it with the new one.
        # (You can remove the next 5 lines if u want to keep the old image along with the new one)
        old_image_path = os.path.join(current_directory, '..', relative_path, checked_user['user_image_id'])
        # Check if the old image file exists and it's not the default image before trying to delete it
        if os.path.exists(old_image_path) and checked_user['user_image_id'] not in['female_default_user.jpg', 'male_default_user_jpg']:
            # Delete the old image file
            os.remove(old_image_path)

    # Validate location's image if the user didnt update it, then use the old one:
    elif 'user_image' not in form_files or form_files['user_image'].filename == '':
        image_id =  checked_user['user_image_id']

    data['user_image_from_form'] = image_id
    return data, validation_errors



# Validations for the change_user_account_password method.
def validate_change_user_account_password(form_data):
    PASSWORD_REGEX = re.compile(r'^(?=.*\d)(?=.*\W)(?=.*[A-Z]).+$')
    bcrypt = Bcrypt()  # Create an instance of the Bcrypt class
    validation_errors = []

    data = {
        'old_password_from_form': form_data['old_password'],
        'new_password_from_form': form_data['new_password'],
        'confirm_new_passwrd_from_form': form_data['confirm_new_password'], 
        'user_id_from_session': session['user_id']
    }

    # The next 3 if statements is to validate the old passord input: 
    if len(form_data['old_password']) < 1:
        validation_errors.append(("Please, enter your password.", 'old_password'))
        return data, validation_errors

    if len(form_data['old_password']) < 10:
        validation_errors.append(("Definitely your old password isn't this short!", 'old_password'))
        return data, validation_errors

    mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
    password_query = "SELECT password from users where user_id = %(user_id_from_session)s;"
    result = mysql.query_db(password_query, data)
    if not bcrypt.check_password_hash(result[0]['password'], form_data['old_password']):
        validation_errors.append(("That's not your old password!", 'old_password'))
        return data, validation_errors

    # The next if statements is to validate the new password input:
    if len(form_data['new_password']) < 1:
        validation_errors.append(("Please, enter your new password.", 'new_password'))
        return data, validation_errors

    if len(form_data['new_password']) < 10:
        validation_errors.append(("The new password must be at least 10 characters.", 'new_password'))
        # return data, validation_errors

    if not PASSWORD_REGEX.match(form_data['new_password']):
        validation_errors.append((
            "The new password must contain at least one digit, one symbol, and one uppercase letter.", 'new_password'
        ))
        return data, validation_errors

    # The next if statements is to validate the "confirm new password" input:
    if form_data['new_password'] != form_data['confirm_new_password']:
        validation_errors.append(("Passwords do not match!", 'confirm_new_password'))

    return data, validation_errors




# /////////////////////////////////////////////////  Posts Validations  ///////////////////////////////////////////////
# //////////////////////////////////////////////// ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ /////////////////////////////////////////////////


# Validations for the add_new_post method.
def validate_add_new_post_method(form_data, form_files):
    validation_errors = []
    data = {
        'user_id_from_session': session['user_id']
    }

    # If the caption is missed or the uploaded post was empty (empty caption & no media), which means front-end validations failed.
    if ('post_form_caption' not in form_data) or (form_data.get('post_form_caption') == "" and len(form_files) == 0):
        validation_errors.append(("An error occured while uploading your comment, try again.", 'fail'))
        return data, validation_errors

    data['caption_from_form'] = form_data.get('post_form_caption').strip()

    # If the post has media files uploaded with it, then validate their type and size.
    if form_files.getlist('images[]') and len(form_files.getlist('images[]')) > 0:
        media_files = form_files.getlist('images[]')


        # Validate type of each media file before saving any of them.
        # If any one of them fail then that means frontend validations failed, and it will not save any of them.
        for media_file in media_files:
            media_type = media_file.content_type.split('/')
            if not validate_type_of_uploaded_media_file(media_type):
                validation_errors.append(("An uploaded file type is not acceptable.", 'fail'))
                return data, validation_errors

        data['added_media_names'] = {}
        media_paths = []
        for media_file in media_files:
            #Extract the type of the media.
            media_type = media_file.content_type.split("/")[0]
            # Define the relative path to the target directory.
            relative_path = 'static/uploads/posts/{}s'.format(media_type)
            # Construct the complete path to save the media.
            media_path = os.path.join(current_directory, '..', relative_path)
            # Process the uploaded media.
            original_filename = secure_filename(media_file.filename)
            # Generate a unique filename (image_id) using UUID.
            media_name = f"{uuid.uuid4()}_{original_filename}"
            data['added_media_names'][media_name] = media_type
            # Append the media_id to the path.
            media_path = os.path.join(media_path, media_name)
            # Save the media file.
            media_file.save(media_path)
            media_paths.append(media_path)

        # Validate size of media file.
        for media_path in media_paths:
            if not validate_size_of_uploaded_media_file(media_path, media_path.split("/")[-2][:-1]):
                validation_errors.append(("An uploaded file size is above the maximum.", 'fail'))
                # If any one of them fail then that means frontend validations failed, and it will not save any of them.
                # Remove all the saved medias above from the server.
                for media in media_paths:
                    if os.path.exists(media):
                        os.remove(media)
                return data, validation_errors

        # Add the new media files to the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        # Construct the INSERT INTO query with properly formatted tuples
        add_new_post_media_query = """
            INSERT INTO media (name, type, reference_table, reference_id) VALUES {}
        """.format(', '.join(["('{}', '{}', 'posts', %(updated_post_id)s)".format(name, media_type) for name, media_type in data['added_media_names'].items()]))

        # Execute the query
        mysql.query_db(add_new_post_media_query, data)

    return data, validation_errors



# Validations for the update_post method.
def validate_update_post_method(form_data, form_files):
    validation_errors = []
    data = {
        'updated_post_id': form_data['updated_post_id'],
    }

    is_valid_update = False

    # Check if the caption is totally missed.
    if 'update_post_form_caption' not in form_data:
        validation_errors.append(("An error occured while updating your post, try again.", 'fail'))
        return data, validation_errors

    # Check the updated post caption is not missed or totally empty:
    else:
        data['updated_post_caption'] = form_data.get('update_post_form_caption').strip()
        is_valid_update = True

    # If the user added new media to the post.
    if form_files.getlist('added_images[]') and len(form_files.getlist('added_images[]')) != 0:
        is_valid_update = True
        media_files = form_files.getlist('added_images[]')

        # Validate type of each media file before saving any of them.
        # If any one of them fail then that means frontend validations failed, and it will not save any of them.
        for media_file in media_files:
            media_type = media_file.content_type.split('/')
            if not validate_type_of_uploaded_media_file(media_type):
                validation_errors.append(("An uploaded file type is not acceptable.", 'fail'))
                return data, validation_errors

        data['added_media_names'] = {}
        media_paths = []
        for media_file in media_files:
            #Extract the type of the media.
            media_type = media_file.content_type.split("/")[0]
            # Define the relative path to the target directory.
            relative_path = 'static/uploads/posts/{}s'.format(media_type)
            # Construct the complete path to save the media.
            media_path = os.path.join(current_directory, '..', relative_path)
            # Process the uploaded media.
            original_filename = secure_filename(media_file.filename)
            # Generate a unique filename (image_id) using UUID.
            media_name = f"{uuid.uuid4()}_{original_filename}"
            data['added_media_names'][media_name] = media_type
            # Append the media_id to the path.
            media_path = os.path.join(media_path, media_name)
            # Save the media file.
            media_file.save(media_path)
            media_paths.append(media_path)

        # Validate size of media file.
        for media_path in media_paths:
            if not validate_size_of_uploaded_media_file(media_path, media_path.split("\\")[-2][:-1]):
                validation_errors.append(("An uploaded file size is above the maximum.", 'fail'))
                # If any one of them fail then that means frontend validations failed, and it will not save any of them.
                # Remove all the saved medias above from the server.
                for media in media_paths:
                    if os.path.exists(media):
                        os.remove(media)
                return data, validation_errors

        # Add the new media files to the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        # Construct the INSERT INTO query with properly formatted tuples
        add_new_post_media_query = """
            INSERT INTO media (name, type, reference_table, reference_id) VALUES {}
        """.format(', '.join(["('{}', '{}', 'posts', %(updated_post_id)s)".format(name, media_type) for name, media_type in data['added_media_names'].items()]))

        # Execute the query
        mysql.query_db(add_new_post_media_query, data)

    # If the user deleted some media from the original media of the post.
    if form_data.getlist('deleted_images[]') and len(form_data.getlist('deleted_images[]')) > 0:
        # Get the names of the original post media files.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        post_original_media_names_query = """
            SELECT name AS post_media_name FROM media WHERE reference_table = "posts" AND reference_id = %(updated_post_id)s;
        """
        post_original_media_names = mysql.query_db(post_original_media_names_query, data)
        # Extract values of 'post_media_name' key from each dictionary and store them in a set.
        post_original_media_names = {name['post_media_name'] for name in post_original_media_names}

        # Check if the deleted file names are within the names of the original post, so their will be no chance of deleteing other post's media in any way.
        for deleted_media_name in form_data.getlist('deleted_images[]'):
            if deleted_media_name.split("/")[-1] not in post_original_media_names:
                validation_errors.append(("Something is wrong, the deleted media is not in the original post to delete it!", 'fail'))
                return data, validation_errors

        # If everything is ok with the deleted media then delete them from the server:
        is_valid_update = True

        # Delete the deleted media files from the server
        data['deleted_media'] = form_data.getlist('deleted_images[]')
        data['deleted_media_names'] = []
        for media in data['deleted_media']:
            # Extract the name of the media.
            data['deleted_media_names'].append(media.split("/")[-1])
            # Remove the first backslash from the media so the next path.join work properly.
            media = media[1:]
            # Construct the path to the media to delete it.
            media_path = os.path.join(current_directory, '..', media)
            # Check if the media_path file exists.

            if os.path.exists(media_path):
                os.remove(media_path)

        # Delete the deleted media files from the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        # Construct the DELETE FROM query with properly formatted media names
        delete_removed_post_media_query = """
            DELETE FROM media WHERE name IN ({})
        """.format(', '.join(["'{}'".format(media_name) for media_name in data['deleted_media_names']]))

        # Execute the query
        mysql.query_db(delete_removed_post_media_query)

    if not is_valid_update:
        validation_errors.append(("An error occured while updating your reply, try again.", 'fail'))

    return data, validation_errors




# ///////////////////////////////////////////////  Comments Validations  ///////////////////////////////////////////////
# //////////////////////////////////////////////// ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ /////////////////////////////////////////////////


# Validations for add_new_comment method.
def validate_add_new_comment_method(form_data, form_files):
    validation_errors = []
    data = {
        'post_id_from_form': int(form_data['post_id_of_comment']),
        'user_id_from_session': session['user_id']
    }

    # If the caption is missed or the uploaded comment was empty (empty caption & no media), which means front-end validations failed.
    if ('comment_form_caption' not in form_data) or (form_data.get('comment_form_caption') == "" and len(form_files) == 0):
        validation_errors.append(("An error occured while uploading your comment, try again.", 'fail'))
        return data, validation_errors

    data['caption_from_form'] = form_data.get('comment_form_caption').strip()

    # If the comment has only one media file (as it must be).
    if form_files.getlist('images[]'):
        if len(form_files.getlist('images[]')) == 1:
            media_file = form_files.getlist('images[]')[0]
            media_type = media_file.content_type.split('/')

            # Validate type of media file.
            if not validate_type_of_uploaded_media_file(media_type):
                validation_errors.append(("An uploaded file type is not acceptable.", 'fail'))
                return data, validation_errors

            # Define the relative path to the target directory (one level up).
            relative_path = 'static/uploads/comments/{}s'.format(media_type[0])
            # Construct the complete path to save the media.
            media_path = os.path.join(current_directory, '..', relative_path)
            # Process the uploaded media.
            original_medianame = secure_filename(media_file.filename)
            # Generate a unique filename (media_name) using UUID.
            media_name = f"{uuid.uuid4()}_{original_medianame}"
            # Append the media_id to the path.
            media_path = os.path.join(media_path, media_name)
            # Save the file.
            media_file.save(media_path)

            # Validate size of media file.
            if not validate_size_of_uploaded_media_file(media_path, media_type[0]):
                validation_errors.append(("An uploaded file size is above the maximum.", 'fail'))
                # Remove the media file from the server.
                os.remove(media_path)
                return data, validation_errors

            data['media_name'] = media_name
            data['media_type'] = media_type[0]

        # If the comment has more than one media file (this is not normal).
        else:
            validation_errors.append(("An error occured while uploading your comment, try again.", 'fail'))
            return data, validation_errors

    return data, validation_errors



# Validations for the update_comment method.
def validate_update_comment_method(form_data, form_files):
    validation_errors = []
    data = {
        'updated_comment_id': form_data['updated_comment_id']
    }

    is_valid_update = False

    # Check if the caption is totally missed.
    if 'update_comment_form_caption' not in form_data:
        validation_errors.append(("An error occured while updating your comment, try again.", 'fail'))
        return data, validation_errors

    # Check the updated comment caption is not missed or totally empty:
    else:
        data['updated_comment_caption'] = form_data.get('update_comment_form_caption').strip()
        is_valid_update = True

    # If the user added new media, and only one media file to the comment.
    if form_files.getlist('added_images[]') and len(form_files.getlist('added_images[]')) == 1:
        is_valid_update = True

        media_file = form_files.getlist('added_images[]')[0]
        media_type = media_file.content_type.split('/')

        # Validate type of media file.
        if not validate_type_of_uploaded_media_file(media_type):
            validation_errors.append(("An uploaded file type is not acceptable.", 'fail'))
            return data, validation_errors
        
        # Define the relative path to the target directory (one level up).
        relative_path = 'static/uploads/comments/{}s'.format(media_type[0])
        # Construct the complete path to save the media.
        media_path = os.path.join(current_directory, '..', relative_path)
        # Process the uploaded media.
        original_medianame = secure_filename(media_file.filename)
        # Generate a unique filename (media_name) using UUID.
        media_name = f"{uuid.uuid4()}_{original_medianame}"
        # Append the media_id to the path.
        media_path = os.path.join(media_path, media_name)
        # Save the file.
        media_file.save(media_path)

        # Validate size of media file.
        if not validate_size_of_uploaded_media_file(media_path, media_type[0]):
            validation_errors.append(("An uploaded file size is above the maximum.", 'fail'))
            # Remove the media file from the server.
            os.remove(media_path)
            return data, validation_errors

        # Since each comment can only has one media file, then we will delete any relatable media file record from DB before adding any new one.
        # Check if there is any media associated with the comment and get it's name and type.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        comment_original_media_names_query = """
            SELECT name, type FROM media WHERE reference_table = "comments" AND reference_id = %(updated_comment_id)s;
        """
        comment_original_media_name_and_type = mysql.query_db(comment_original_media_names_query, data)
        if len(comment_original_media_name_and_type) == 1:
            comment_original_media_name_and_type = comment_original_media_name_and_type[0]

            # Delete any assosiated media record from the DB.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            delete_associated_media_query = """
                DELETE from media WHERE reference_table = 'comments' AND reference_id = %(updated_comment_id)s;
            """        
            mysql.query_db(delete_associated_media_query, data)

            # Delete any assosiated media file from the server.
            relative_path = 'static/uploads/comments/{}s/{}'.format(comment_original_media_name_and_type['type'], comment_original_media_name_and_type['name'])
            media_path = os.path.join(current_directory, '..', relative_path)
            if os.path.exists(media_path):          
                os.remove(media_path)

        data['new_media_name'] = media_name
        data['new_media_type'] = media_type[0]
        # Add the new media files to the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        # Construct the INSERT INTO query with properly formatted tuples
        add_new_comment_media_query = """
            INSERT INTO media (name, type, reference_table, reference_id) VALUES (%(new_media_name)s, %(new_media_type)s, 'comments', %(updated_comment_id)s)
        """
        mysql.query_db(add_new_comment_media_query, data)


    # If the user deleted some media from the original media of the comment.
    elif form_data.getlist('deleted_images[]') and len(form_data.getlist('deleted_images[]')) == 1:
        # Get the names of the original comment media file.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        comment_original_media_name_query = """
            SELECT name AS comment_media_name FROM media WHERE reference_table = "comments" AND reference_id = %(updated_rcomment_id)s;
        """
        comment_original_media_name = mysql.query_db(comment_original_media_name_query, data)
        if len(comment_original_media_name) == 1:
            comment_original_media_name = comment_original_media_name[0]['comment_media_name']

        # Check if the deleted file name is the same as the original comment's media name, so their will be no chance of deleteing other comment's media in any way.
        if form_data.getlist('deleted_images[]')[0].split("/")[-1] != comment_original_media_name:
                validation_errors.append(("Something is wrong, the deleted media is not in the original comment to delete it!", 'fail'))
                return data, validation_errors

        # If everything is ok with the deleted media then delete them from the server:
        is_valid_update = True

        # Delete the deleted media files from the server
        media = form_data.getlist('deleted_images[]')[0]
        media = media[1:]
        media_path = os.path.join(current_directory, '..', media)
        if os.path.exists(media_path):          
            os.remove(media_path)

        # Delete the deleted media record from the database.
        data = { 'deleted_media_name': form_data.getlist('deleted_images[]')[0].split("/")[-1] }
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        delete_removed_comment_media_query = """
            DELETE FROM media WHERE name = %(deleted_media_name)s;
        """
        # Execute the query
        mysql.query_db(delete_removed_comment_media_query, data)

    if not is_valid_update:
        validation_errors.append(("An error occured while updating your comment, try again.", 'fail'))

    return data, validation_errors




# ////////////////////////////////////////////////  Replys Validations /////////////////////////////////////////////////
# //////////////////////////////////////////////// ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ /////////////////////////////////////////////////


# Validations for the add_new_reply method.
def validate_add_new_reply_method(form_data, form_files):
    validation_errors = []
    data = {
        'comment_id_from_form': int(form_data['comment_id_of_reply']),
        'user_id_from_session': session['user_id']
    }

    # If the caption is missed or the uploaded reply was empty (empty caption & no media), which means front-end validations failed.
    if ('reply_form_caption' not in form_data) or (form_data.get('reply_form_caption') == "" and len(form_files) == 0):
        validation_errors.append(("An error occured while uploading your reply, try again.", 'fail'))
        return data, validation_errors
    
    data['caption_from_form'] = form_data.get('reply_form_caption').strip()

    # If the reply has only one media file (as it must be).
    if form_files.getlist('images[]'):
        if len(form_files.getlist('images[]')) == 1:
            media_file = form_files.getlist('images[]')[0]
            media_type = media_file.content_type.split('/')

            # Validate type of media file.
            if not validate_type_of_uploaded_media_file(media_type):
                validation_errors.append(("An uploaded file type is not acceptable.", 'fail'))
                return data, validation_errors

            # Define the relative path to the target directory (one level up).
            relative_path = 'static/uploads/replies/{}s'.format(media_type[0])
            # Construct the complete path to save the media.
            media_path = os.path.join(current_directory, '..', relative_path)
            # Process the uploaded media.
            original_medianame = secure_filename(media_file.filename)
            # Generate a unique filename (media_name) using UUID.
            media_name = f"{uuid.uuid4()}_{original_medianame}"
            # Append the media_id to the path.
            media_path = os.path.join(media_path, media_name)
            # Save the file.
            media_file.save(media_path)

            # Validate size of media file.
            if not validate_size_of_uploaded_media_file(media_path, media_type[0]):
                validation_errors.append(("An uploaded file size is above the maximum.", 'fail'))
                # Remove the media file from the server.
                os.remove(media_path)
                return data, validation_errors

            data['media_name'] = media_name
            data['media_type'] = media_type[0]

            # If the reply has more than one media file (this is not normal).
        else:
            validation_errors.append(("An error occured while uploading your reply, try again.", 'fail'))
            return data, validation_errors

    return data, validation_errors



# Validations for the update_reply method.
def validate_update_reply_method(form_data, form_files):
    validation_errors = []
    data = {
        'updated_reply_id': form_data['updated_reply_id']
    }

    is_valid_update = False

    # Check if the caption is totally missed.
    if 'update_reply_form_caption' not in form_data:
        validation_errors.append(("An error occured while updating your reply, try again.", 'fail'))
        return data, validation_errors

    # Check the updated reply caption is not missed or totally empty:
    else:
        data['updated_reply_caption'] = form_data.get('update_reply_form_caption').strip()
        is_valid_update = True

    # If the user added new media, and only one media file to the reply.
    if form_files.getlist('added_images[]') and len(form_files.getlist('added_images[]')) == 1:
        is_valid_update = True

        media_file = form_files.getlist('added_images[]')[0]
        media_type = media_file.content_type.split('/')

        # Validate type of media file.
        if not validate_type_of_uploaded_media_file(media_type):
            validation_errors.append(("An uploaded file type is not acceptable.", 'fail'))
            return data, validation_errors
        
        # Define the relative path to the target directory (one level up).
        relative_path = 'static/uploads/replies/{}s'.format(media_type[0])
        # Construct the complete path to save the media.
        media_path = os.path.join(current_directory, '..', relative_path)
        # Process the uploaded media.
        original_medianame = secure_filename(media_file.filename)
        # Generate a unique filename (media_name) using UUID.
        media_name = f"{uuid.uuid4()}_{original_medianame}"
        # Append the media_id to the path.
        media_path = os.path.join(media_path, media_name)
        # Save the file.
        media_file.save(media_path)

        # Validate size of media file.
        if not validate_size_of_uploaded_media_file(media_path, media_type[0]):
            validation_errors.append(("An uploaded file size is above the maximum.", 'fail'))
            # Remove the media file from the server.
            os.remove(media_path)
            return data, validation_errors

        # Since each reply can only has one media file, then we will delete any relatable media file record from DB before adding any new one.
        # Check if there is any media associated with the reply and get it's name and type.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        reply_original_media_names_query = """
            SELECT name, type FROM media WHERE reference_table = "replies" AND reference_id = %(updated_reply_id)s;
        """
        reply_original_media_name_and_type = mysql.query_db(reply_original_media_names_query, data)
        if len(reply_original_media_name_and_type) == 1:
            reply_original_media_name_and_type = reply_original_media_name_and_type[0]

            # Delete any assosiated media record from the DB.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            delete_associated_media_query = """
                DELETE from media WHERE reference_table = 'replies' AND reference_id = %(updated_reply_id)s;
            """        
            mysql.query_db(delete_associated_media_query, data)

            # Delete any assosiated media file from the server.
            relative_path = 'static/uploads/replies/{}s/{}'.format(reply_original_media_name_and_type['type'], reply_original_media_name_and_type['name'])
            media_path = os.path.join(current_directory, '..', relative_path)
            if os.path.exists(media_path):          
                os.remove(media_path)

        data['new_media_name'] = media_name
        data['new_media_type'] = media_type[0]
        # Add the new media files to the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        # Construct the INSERT INTO query with properly formatted tuples
        add_new_reply_media_query = """
            INSERT INTO media (name, type, reference_table, reference_id) VALUES (%(new_media_name)s, %(new_media_type)s, 'replies', %(updated_reply_id)s)
        """
        mysql.query_db(add_new_reply_media_query, data)


    # If the user deleted some media from the original media of the reply.
    elif form_data.getlist('deleted_images[]') and len(form_data.getlist('deleted_images[]')) == 1:
        # Get the names of the original reply media file.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        reply_original_media_name_query = """
            SELECT name AS reply_media_name FROM media WHERE reference_table = "replies" AND reference_id = %(updated_reply_id)s;
        """
        reply_original_media_name = mysql.query_db(reply_original_media_name_query, data)
        if len(reply_original_media_name) == 1:
            reply_original_media_name = reply_original_media_name[0]['reply_media_name']

        # Check if the deleted file name is the same as the original reply's media name, so their will be no chance of deleteing other reply's media in any way.
        if form_data.getlist('deleted_images[]')[0].split("/")[-1] != reply_original_media_name:
                validation_errors.append(("Something is wrong, the deleted media is not in the original reply to delete it!", 'fail'))
                return data, validation_errors

        # If everything is ok with the deleted media then delete them from the server:
        is_valid_update = True

        # Delete the deleted media files from the server
        media = form_data.getlist('deleted_images[]')[0]
        media = media[1:]
        media_path = os.path.join(current_directory, '..', media)
        if os.path.exists(media_path):          
            os.remove(media_path)

        # Delete the deleted media record from the database.
        data = { 'deleted_media_name': form_data.getlist('deleted_images[]')[0].split("/")[-1] }
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        delete_removed_reply_media_query = """
            DELETE FROM media WHERE name = %(deleted_media_name)s;
        """
        # Execute the query
        mysql.query_db(delete_removed_reply_media_query, data)

    if not is_valid_update:
        validation_errors.append(("An error occured while updating your reply, try again.", 'fail'))

    return data, validation_errors




# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# Function to check if media files exist in the server & delete them when deleting the related post or comment or reply.
def validate_deleted_media_files(all_media):
    for media in all_media:
        if media['name'] is not None and media['type'] is not None:
            # Define the relative path to the target directory (one level up).
            relative_path = r"..\static\uploads\{}\{}s".format(media['reference_table'], media['type'])
            # Construct the path to the media to replace it with the new one.
            media_path = os.path.join(current_directory, relative_path, media['name'])
            # Check if the media_path file exists.
            if os.path.exists(media_path):
                os.remove(media_path)

# Validate the type of the uploaded media files.
def validate_type_of_uploaded_media_file(file_type, allowed_types={ 'image': ('apng', 'bmp', 'gif', 'jpeg', 'jpg', 'png', 'webp', 'svg'), 'video':('mp4', 'webm', 'ogg') }):
    if len(file_type) == 2:  # Ensure valid format
        media_category = file_type[0].lower()
        media_format = file_type[1].lower()
        if media_category in allowed_types and media_format in allowed_types[media_category]:
            return True
    return False

# Validate the size of the uploaded media files.
def validate_size_of_uploaded_media_file(file_path, file_type, allowed_sizes={ 'image': 25*1024*1024, 'video':500*1024*1024 }):
    if file_type in allowed_sizes and os.stat(file_path).st_size <= allowed_sizes[file_type]:
        return True
    return False

