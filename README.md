# FL-Backend

This is a Django app for FL-Backend. It provides instructions on how to set up a virtual environment, run Docker Compose for the database, migrate the database, and run the app.

## Prerequisites

- Python 3.x
- Docker
- Docker Compose

## Setup

1. Clone the repository:

    ```bash
    git clone <repository_url>
    ```

2. Create a virtual environment:

    ```bash
    python3 -m venv venv
    ```

3. Activate the virtual environment:

    - For Windows:

      ```bash
      venv\Scripts\activate
      ```

    - For macOS/Linux:

      ```bash
      source venv/bin/activate
      ```

4. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Database Setup

1. Start the database using Docker Compose:

    ```bash
    docker-compose up -d
    ```

2. Apply the database migrations:

    ```bash
    python manage.py migrate
    ```

## Running the App

1. Start the Django development server:

    ```bash
    python manage.py runserver
    ```

2. Open your web browser and navigate to `http://localhost:8000` to access the app.

