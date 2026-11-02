SmartStock AI – Inventory Analysis & Reorder Assistant

SmartStock AI is an inventory management and analysis dashboard built using Python, Streamlit, Pandas, and MySQL.

The project helps monitor product stock levels, identify inventory risks, and generate rule-based reorder recommendations.

Features

- Inventory overview dashboard
- Product search and category filters
- Stock status monitoring
- Low-stock and critical-stock identification
- Reorder quantity recommendations
- CSV upload and download
- MySQL database integration

Technologies Used

- Python
- Streamlit
- Pandas
- MySQL
- SQL

How It Works

The application analyses product stock, daily demand, safety stock, and supplier lead time to calculate inventory risk and suggested reorder quantities.

The current recommendation system uses rule-based logic, not a trained machine learning model.

Run Locally

Install dependencies:

pip install -r requirements.txt

Start the application:

python -m streamlit run app.py

Database

The project supports loading inventory data from a MySQL database.

Configure your database credentials using environment variables. Never publish passwords or private credentials in this repository.

Project Type

Beginner-level portfolio project demonstrating Python-based data analysis, SQL database integration, and dashboard development.

Author

Developed as a portfolio project to practise data analysis and inventory management concepts.
