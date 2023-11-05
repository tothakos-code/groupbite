# order-accumulator
Order Accumulator is a project designed to facilitate the logistics of food ordering from falusitekercs.hu in Szeged.

The entire project is configured to run within a Docker Compose environment and is developer-friendly.

## Getting Started

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
3. Start the project
  ```bash
  docker-compose up -d
  ```

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
