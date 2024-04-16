<div align="center">
  <h1> Ultimate Inventory </h1>
</div>


Introducing "Ultimate Inventory," the next evolution of our previous project, [Prime Inventory](https://github.com/OsamaTbaileh/PrimeInventory). Packed with enhanced features, improved performance, and fortified security measures, it sets a new standard in inventory management.

## what's new?
- **📊 Dynamic Dashboard:** Empower users with a streamlined feed for posting, commenting, replying, and liking to enhance communication and collaboration between teams and users.
- **🖼️ Media Files Upload:** Additionally, users can seamlessly upload media files such as images and videos, enhancing efficiency in managing inventory operations.
- **💾 Enhanced Database Efficiency:** Improve database performance, strengthen validations, and refine backend logic.
- **🚀 Expanded API Integration:** Integrate Gmail and Google Maps APIs to elevate functionality and user experience.


## Idea:
This web application is specifically designed to assist store managers in efficiently managing multiple warehouses located in different cities and locations. In addition to providing a streamlined solution for organizing products within these warehouses and tracking their movement, it also includes a feature for building teams composed of various workers and managers. By enabling collaboration among team members, the application enhances operational efficiency and optimizes inventory management processes. Moreover, it helps maintain accurate records of product movement within the company's warehousing infrastructure.


## Functional Specifications:
- **Fully Responsive:** The usage of Bootstrap makes it suitable for all screen sizes.
- **Login and Registration:** The application supports two types of authentication: worker and manager accounts.
  - Worker Account:
    - Limited access to website functionalities.
    - Can add new products to the system.
  - Manager Account:
    - Higher permissions and privileges.
    - Can add, delete, and modify various entities (locations, products, etc.).
    - Can observe the movements of all products.
  - Admin Account:
    - Highest permissions and privileges.
    - Can delete users accounts.


## Programming Languages, Frameworks & Libraries Used:
- Python 3.6.4
- Flask 2.0.3
- MySQL Workbench 8.0 CE
- Bootstrap 5.0.2 


## Data Base:
-SQL Through MySQL Workbench.


## Color Schema:

:-------------------------:|:-------------------------:
![](https://github.com/OsamaTbaileh/PrimeInventory/blob/main/static/assets/home_page.jpeg)  |  ![](https://github.com/OsamaTbaileh/PrimeInventory/blob/main/static/assets/home_page.jpeg)


<br/>


## Some Screenshots of The Website:
## Home Page:
![Home Page Screenshot](https://github.com/OsamaTbaileh/PrimeInventory/blob/main/static/assets/home_page.jpeg)

<br/><br/>

## Locations Page:
![Locations Page Screenshot](https://github.com/OsamaTbaileh/PrimeInventory/blob/main/static/assets/locations_page.jpeg)

<br/><br/>

## Products Page:
![Products Page Screenshot](https://github.com/OsamaTbaileh/PrimeInventory/blob/main/static/assets/products_page.jpeg)

<br/><br/>

## Movements Page:
![Movements Page Screenshot](https://github.com/OsamaTbaileh/PrimeInventory/blob/main/static/assets/movements_page.jpeg)

<br/><br/>

## Normal Report Page:
![Report Page Screenshot](https://github.com/OsamaTbaileh/PrimeInventory/blob/main/static/assets/normal_report_page.jpeg)

<br/><br/>

## Advanced Report Page:
![Report Page Screenshot](https://github.com/OsamaTbaileh/PrimeInventory/blob/main/static/assets/advanced_report_page.jpeg)

<br/><br/>

## ERD:
![ERD Diagram](https://github.com/OsamaTbaileh/PrimeInventory/blob/main/static/assets/ERD_diagram.jpg)

<br/><br/>

## Getting Started:
"Ultimate Inventory" requires [Python](https://www.python.org/downloads/) to run.
1. **Clone the repository** to your local machine, open ur cmd & write down:
```sh
git clone <https://github.com/OsamaTbaileh/UltimateInventory>
```
2. **Activate your virtual environment**. If you don't have a virtual environment set up, create and activate one using the appropriate commands for your operating system. The following commands are to make a new environment and to activate it:
```sh
Python -m venv                  ex: Python -m myEnv
call myEnv/Scripts/activate
```
3. **Install Flask and dependencies**:
Make sure your virtual environment is activated and in your cmd write down:
```sh
pip install Flask
```
4. **Navigate to the project directory** containing the Flask app's entry point file (`server.py`):
```sh
cd path/to/entry/UltimateInventory
```
5. **Start the server**:
```sh
python server.py
```
6. Open your web browser and visit the specified URL or endpoint to access the web app.(Usually, it's localhost:5000):
```sh
localhost:5000
```
<br/>


## Support
If you encounter any issues or have questions, please [submit an issue](https://github.com/OsamaTbaileh/UltimateInventory/issues) or contact me on one of my contacts [HERE](https://github.com/OsamaTbaileh/OsamaTbaileh)
### Note:
- login and registration will be added very soon, stay tuned.
