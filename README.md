# MARKET PROZORRO UA
REST API application for managing Criteria and Profile

## Requirements
To run this application on system must be installed [Docker](https://www.docker.com/)

## Run
To start application make you follow next steps:
1. Clone this repository
    ```bash
    git clone git@github.com:openprocurement/market.prozorro.ua.git market_prozorro_ua
    ```
2. Changed working directory
    ```bash
    cd market_prozorro_ua
    ```
3. Run application
    ```bash
    docker-compose up --build --force-recreate -d
    ```
4. Run migrations
    ```bash
    docker-compose exec web bash -c './manage.py migrate'
    ```

## Authorization
Included test storage with following credentials:
| Username | Password      |
| -------- | ------------- |
| admin    | adminpassword |
| user     | userpassword  |

## Update
1. Stop containers
    ```bash
    docker-compose down
    ```
2. Pull changes from repository
    ```bash
    git pull origin master
    ```
3. Run application
    ```bash
    docker-compose up --build --force-recreate -d
    ```
4. Run migrations
    ```bash
    docker-compose exec web bash -c './manage.py migrate'
    ```
