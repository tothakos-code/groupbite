# order-accumulator
This project is an web application that may helps you and your friend ordering pizza or other food for a party or just for work.

The entire project is configured to run within a Docker Compose environment and is developer-friendly.

## Getting Started

__Notice__: Currently this repo is in an unstable state. It has a lot of skecthes, proof of concept solutions for 2.0. Expect a lot of error and rapid changes to files and database structures in the near future.

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

    Python version: 3.11

    ```bash
    python -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    python app.py
    ```

4. Start your frontend

    ```bash
    cd frontend
    npm run serve
    ```

5. Start the database

    The database at this stage of the developmet for 2.0 is:
    ```bash
    docker-compose up -d database
    ```

6. Start the backend
    in another terminal

    ```bash
    python run.py
    ```

You can make changes to the fronend files and it will reload the frontned on save. Same is true for the backend.

## Notice
In a production environment, it is not recommended to use Nginx and the Database within Docker. Instead, consider using versions directly installed on the server. Adjust your production deployment accordingly.

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
