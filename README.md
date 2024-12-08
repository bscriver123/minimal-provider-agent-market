# Minimal provider Agent Market

## Running the service locally

In order to test the service locally, you can build the Docker image and run the service with the following commands:

```shell
docker build -t test .
docker run --env-file .env test python -m src.market_scan
docker run --env-file .env test python -m src.solve_instances
```
