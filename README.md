[![Build Status](https://travis-ci.org/dann254/fancy-shoppinglist-API.svg?branch=master)](https://travis-ci.org/dann254/fancy-shoppinglist-API)
[![Coverage Status](https://coveralls.io/repos/github/dann254/fancy-shoppinglist-API/badge.svg?branch=master)](https://coveralls.io/github/dann254/fancy-shoppinglist-API?branch=master)
[![Code Health](https://landscape.io/github/dann254/fancy-shoppinglist-API/master/landscape.svg?style=flat)](https://landscape.io/github/dann254/fancy-shoppinglist-API/master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/08bdac7809b94946b3f3621d83a86f62)](https://www.codacy.com/app/dann254/fancy-shoppinglist-API?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dann254/fancy-shoppinglist-API&amp;utm_campaign=Badge_Grade)
# fancy-shoppinglist-API
This is an innovative shopping list app that allows users to record and share things they want to spend money on. The app keeps track of their shopping lists. it is implemented as a flask RESTful API

# installation procedure.
  1. Ensure you have *python 3*, *virtualenv*,*postgresql* and *pip* installed on your local machine.
  2. You might also need an app to test the API i.e *postman*
  3. Clone the project locally. and create a postgres database like `my_db`
  4. navigate to the project folder.
  5. create a virtual environment. example `mkvirtualenv fancy`
  6. create a `.env` file and change the first line to the environment you just created. i.e`workon fancy`. PS you might need to edit it based on your operating system. like

  ```
  workon api
  export SECRET="random_key"
  export APP_SETTINGS="development"
  export DATABASE_URL="postgresql:///my_db"
  ```

  7. Run `source .env` if you are on unix or find the equivalent on windows.
  8. install the requirements in the environment. `pip install -r requirements.txt`

# Running the app
  1. `python run.py`
  2. For endpoints that require tokens user Key:`Auth`, Value:`Bearer TOKEN`

# Swagger documentation
  ![View documentation](https://app.swaggerhub.com/apis/dann254/fancy-shoppinglist-API/1.0.0 "")

# Hosted on heroku
  https://fancy-shoppinglist-api.herokuapp.com/

#### API Endpoints

  | URL                                              | Methods | Description              | Requires Token |
  |--------------------------------------------------|---------|--------------------------|----------------|
  | /auth/register/                                  | POST    | registering a user       | FALSE          |
  | /auth/login/                                     | POST    | User login               | FALSE          |
  | /user/                                           | GET     | Get user profile         | TRUE           |
  | /user/                                           | PUT     | Edit username            | TRUE           |
  | /user/                                           | DELETE  | Delete a user account    | TRUE           |
  | /shoppinglists/                                  | POST    | Creates shoppinglist     | TRUE           |
  | /shoppinglists/                                  | GET     | Gets all shoppinglists   | TRUE           |
  | /shoppinglists/<int:list_id>                     | PUT     | Edit a shoppinglist name | TRUE           |
  | /shoppinglists/<int:list_id>                     | DELETE  | Delete a shoppinglist    | TRUE           |
  | /shoppinglists/<int:list_id>                     | GET     | Get a shoppinglist by id | TRUE           |
  | /shoppinglists/share/<int:list_id>               | PUT     | Change share status      | TRUE           |
  | /shoppinglists/<int:list_id>/items/              | POST    | Create an item           | TRUE           |
  | /shoppinglists/<int:list_id>/items/              | GET     | Get shoppinglist items   | TRUE           |
  | /shoppinglists/<int:list_id>/items/<int:item_id> | PUT     | Edit an item             | TRUE           |
  | /shoppinglists/<int:list_id>/items/<int:item_id> | DELETE  | Delete an item           | TRUE           |
  | /shoppinglists/<int:list_id>/items/<int:item_id> | GET     | Get an item by id        | TRUE           |
  | /buddies/                                        | GET     | Get all buddies          | TRUE           |
  | /buddies/                                        | POST    | Invite a buddy           | TRUE           |
  | /buddies/<int:friend_id>                         | GET     | Get buddy by id          | TRUE           |
  | /buddies/<int:friend_id>                         | DELETE  | Unfriend a buddy         | TRUE           |
  | /buddies/shoppinglists/                          | GET     | Get shared shoppinglists | TRUE           |
  | /buddies/shoppinglists/<int:list_id>             | GET     | view items of shared list| TRUE           |
