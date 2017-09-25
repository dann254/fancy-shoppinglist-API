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
