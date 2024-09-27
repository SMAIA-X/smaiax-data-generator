# smaiax-data-generator

## Usage
You can run the data generator together with rabbitmq with the following command:
````shell
docker compose build && docker compose up -d
````

You can specify if AMQP or MQTT should be used. In order to do this set the appropriate protocol in the docker-compose.yml:
```yml
environment:
  - PROTOCOL=MQTT
```

or

```yml
environment:
  - PROTOCOL=AMQP
```

If you use AMQP use the dashboard on [http://localhost:15672](http://localhost:15672).
For MQTT you can use MQTT Explorer or any other tool.
The connection information are provided in the docker-compose.yml