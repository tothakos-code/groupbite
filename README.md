# order-accumulator

This is a web application that aims for food orders for a group of friends. You can create multiple restaurants and manage its menu and menu items, prices.

## Getting Started

__Notice__: With the release of 2.0 the support for 1.x version will end. The release can be expected in 2024 june.

To quickly get started with the project, follow these steps:


1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/order-accumulator.git
    cd order-accumulator
    ```

2. Create a .env file from the example and adjust the settings if needed.

    ```bash
    cp .env.example .env
    ```

3. Setup python virtual environment for the project and install the requirements

    Tested with Python version: 3.10+

    ```bash
    python -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    ```

4. Setup your frontend

    A minimum of node version 16 is required

    ```bash
    cd frontend
    npm install
    npm run serve
    ```

5. Start the database

    The database at this stage of the development for 2.0 is:

    ```bash
    docker-compose up -d database
    ```



6. Start the backend in another terminal

    ```bash
    python run.py
    ```

You can make changes to the frontend files and it will reload the frontend on save. Same is true for the backend.

## Notice

In a production environment, it is not recommended to use Database within Docker its meant for development environment only. Instead, consider using versions directly installed on the server. Adjust your production deployment accordingly.

## Contributing

If you would like to contribute to the project, please follow these guidelines:

1. Fork the repository.

2. Create a new branch for your feature or bug fix:

  ```bash
  git checkout -b feature/new-feature
  ```

3. Make your changes and commit them:

  ```bash
  git commit -am 'Add a new feature'
  ```

4. Push your changes to your fork:

  ```bash
  git push origin feature/new-feature
  ```

5. Open a pull request against the main repository.

## License

This project is licensed under the MIT License.
