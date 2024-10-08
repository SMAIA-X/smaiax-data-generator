# smaiax-data-generator

## Usage
You can run the data generator together with hivemq with the following command:
````shell
docker compose build && docker compose up -d
````

You can access the dashboard on [http://localhost:15672](http://localhost:15672).
The username is `admin` and the password is `hivemq`.
You can also use the mqtt explorer. By default hivemq doesn't have a username or password configured for the mqtt connection.