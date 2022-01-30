
# Points Redemption - Backend Software Engineering


This Project allows financiers to input and keep track of transactions in an SQL database. Users may then redeem the points they accumulate.


## Adding Transactions, Redeeming Points, and Viewing your Balance
- These actions can be completed by submitting HTTP Requests
## Walk-Through/Unit Tests
I use Postman to send my requests. Guide on Postman below.
- Open a terminal in the working directory of the repository and run start.py
- Adding Transactions
    - Send a PUT request containing your transactions in a .json file to http://127.0.0.1:5000/add_transactions
- Redeeming Points
    - Send a PUT request containing the amount of points to spend in a .json file to http://127.0.0.1:5000/spend_points
- Showing Balance
    - Send a GET request to http://127.0.0.1:5000/show_balance
- To view your database
    - Send a GET request to http://127.0.0.1:5000/show_db
- If you would like to clear your database and restart
    - Send a PUT request to http://127.0.0.1:5000/clear_db

## Postman Guide
- Go to: https://web.postman.co/
- Create an account
- Click create new, then HTTP Request
    - You may have to download Postman Agent to do this in browser. It will prompt you to do so
- Use the dropdown to select a GET or PUT Request
- Enter Request URL as one of the URL's given
- To send a .json
    - Click Body, then the raw radio button, then JSON from the dropdown
    - Paste the text of your JSON and click the Send button
## Adding Transactions JSON
[
  {
    "payer": "DANNON",
    "points": 1000,
    "timestamp": "2020-11-02T14:00:00Z"
  },
  {
    "payer": "UNILEVER",
    "points": 200,
    "timestamp": "2020-10-31T11:00:00Z"
  },
  {
    "payer": "DANNON",
    "points": -200,
    "timestamp": "2020-10-31T15:00:00Z"
  },
  {
    "payer": "MILLER COORS",
    "points": 10000,
    "timestamp": "2020-11-01T14:00:00Z"
  },
  {
    "payer": "DANNON",
    "points": 300,
    "timestamp": "2020-10-31T10:00:00Z"
  }
]
## Spend Points JSON
{"points":100}
