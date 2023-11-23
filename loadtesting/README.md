# Load testing

Load testing using https://locust.io/.

Currently, this is run manually on-demand from a developer's laptop.

Steps:

1. Create and activate a venv
2. `pip3 install -r loadtesting/requirements.txt`
3. `locust -f loadtesting/locustfile.py`
4. Go to http://localhost:8089/
5. Start the test and see the results
