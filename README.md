# Gambit Commerce

Gambit Commerce is an e-commerce platform that allows users to easily purchase products. This guide provides the necessary steps to set up and run the project.

## Prerequisites

To run the project, you need to have the following software installed:

- [Python](https://www.python.org/downloads/) (3.8 or higher)
- [Django](https://www.djangoproject.com/download/) (latest version)
- [MySQL](https://dev.mysql.com/downloads/mysql/) (5.7 or higher)
- [pip](https://pip.pypa.io/en/stable/) (Python package manager)

## Project Setup

1. **Download the Project Folder**

   Clone or download the project files from GitHub.

   ```bash
   git clone https://github.com/Gambitdutku/Gambit-Commerce.git
   cd Gambit-Commerce
   ```

2. **Create a Virtual Environment**

   Create and activate a virtual environment to manage the project dependencies.

   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate    # For Windows
   ```

3. **Install Required Packages**

   Install the necessary packages for the project.

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database**

   Place your MySQL dump file in the `sqldump` folder. Then, import the dump into your MySQL database. You can do this using the following command:

   ```bash
   mysql -u yourusername -p yourdatabase < sqldump/shop2.sql
   ```

5. **Run Migrations**

   After setting up the database, run the following command to apply migrations:

   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser (Optional)**

   If you want to access the Django admin panel, create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**

   Start the development server to run the project:

   ```bash
   python manage.py runserver
   ```

8. **Access the Application**

   Open your web browser and go to `http://127.0.0.1:8000/` to access the application.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.