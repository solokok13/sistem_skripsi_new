# Predictive System

A Flask-based web application for predicting student performance.

## Setup Instructions

### Prerequisites

- Python 3.x
- MySQL

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/predictive-system.git
    cd predictive-system
    ```

2. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

3. Activate the virtual environment:
    - **Windows**:
        ```sh
        venv\Scripts\activate
        ```
    - **Mac/Linux**:
        ```sh
        source venv/bin/activate
        ```

4. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

5. Configure the database:
    - Create a MySQL database named `predictive_system`.
    - Create the necessary tables by running the following SQL commands:
        ```sql
        CREATE DATABASE predictive_system;

        USE predictive_system;

        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        );

        CREATE TABLE predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nisn VARCHAR(50),
            nama VARCHAR(100),
            sikap VARCHAR(10),
            peng VARCHAR(10),
            ket VARCHAR(10),
            pts VARCHAR(10),
            pas VARCHAR(10),
            prediction VARCHAR(50),
            user_id INT,
            prediction_time DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        ```

6. Set up the configuration:
    - Create a file named `.env` in the root directory with the following content:
        ```env
        SECRET_KEY=your_secret_key
        MYSQL_HOST=localhost
        MYSQL_USER=root
        MYSQL_PASSWORD=password
        MYSQL_DB=predictive_system
        ```

7. Run the application:
    ```sh
    python run.py
    ```

8. Open a web browser and navigate to `http://localhost:5000`.

## Usage

- **Register**: Create a new user account.
- **Login**: Log in with your credentials.
- **Upload File**: Upload an Excel file with student data for prediction.
- **View History**: View the prediction history and filter by date range.
