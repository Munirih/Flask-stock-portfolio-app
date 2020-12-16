import pytest
from project import create_app
from project.models import Stock, User
from project import database
from datetime import datetime
import requests




########################
#### Helper Classes ####
########################


class MockSuccessResponse(object):
    def __init__(self, url):
        self.status_code = 200
        self.url = url

    def json(self):
        return {
            'Meta Data': {
                "2. Symbol": "AAPL",
                "3. Last Refreshed": "2020-03-24"
            },
            'Time Series (Daily)': {
                "2020-03-24": {
                    "4. close": "148.3400",
                },
                "2020-03-23": {
                    "4. close": "135.9800",
                }
            }
        }


class MockApiRateLimitExceededResponse(object):
    def __init__(self, url):
        self.status_code = 200
        self.url = url

    def json(self):
        return {
            'Note': 'Thank you for using Alpha Vantage! Our standard API call frequency is ' +
                    '5 calls per minute and 500 calls per day.'
        }


class MockFailedResponse(object):
    def __init__(self, url):
        self.status_code = 404
        self.url = url

    def json(self):
        return {'error': 'bad'}


class MockSuccessResponseWeekly(object):
    def __init__(self, url):
        self.status_code = 200
        self.url = url

    def json(self):
        return {
            'Meta Data': {
                "2. Symbol": "AAPL",
                "3. Last Refreshed": "2020-07-28"
            },
            'Weekly Adjusted Time Series': {
                "2020-07-24": {
                    "4. close": "379.2400",
                },
                "2020-07-17": {
                    "4. close": "362.7600",
                },
                "2020-06-11": {
                    "4. close": "354.3400",
                },
                "2020-02-25": {
                    "4. close": "432.9800",
                }
            }
        }



@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()
    flask_app.config.from_object('config.TestingConfig')
    flask_app.extensions['mail'].suppress = True

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context before accessing the logger
        with flask_app.app_context():
            flask_app.logger.info('Creating database tables in test_client fixture...')
        
            # Create the database and the database table(s)
            database.create_all()

        yield testing_client  # this is where the testing happens!
        
        with flask_app.app_context():
            database.drop_all()

@pytest.fixture(scope='module')
def new_stock():
    stock = Stock('AAPL', '16', '406.78', 17, datetime(2020, 7, 18))
    return stock

@pytest.fixture(scope='module')
def new_user():
    user = User('niyammadi@gmail.com', 'Flaskisgreat')
    return user


@pytest.fixture(scope='module')
def register_default_user(test_client):
    user = User('niyammadi@gmail.com', 'Flaskisgreat')
    database.session.add(user)
    database.session.commit()
    return user

@pytest.fixture(scope='function')
def log_in_default_user(test_client, register_default_user):
    # Log in the user
    test_client.post('/users/login',
                     data = {'email': 'niyammadi@gmail.com',
                             'password': 'Flaskisgreat'},
                             follow_redirects=True)
    yield register_default_user # this is where the testing happens!

    #log out the user
    test_client.get('/users/logout', follow_redirects=True)


@pytest.fixture(scope='function')
def confirm_email_default_user(test_client, log_in_default_user):
    # Mark the user as having their email confirmed
    user = User.query.filter_by(email='niyammadi@gmail.com').first()
    user.email_confirmed = True
    user.email_confirmed_on = datetime(2020, 7, 8)
    database.session.add(user)
    database.session.commit()


    yield user   # This is where the testing happens!

    #Mark the user as not having their email confirmed (clean up)
    user = User.query.filter_by(email='niyammadi@gmail.com').first()
    user.email_confirmed = False
    user.email_confirmed_on = None
    database.session.add(user)
    database.session.commit()


@pytest.fixture(scope='function')
def afterwards_reset_default_user_password():
    yield  # this is where the testing happens!

    # Since a test using this fixture could change the password for the default user,
    # reset the password back to the default password
    user = User.query.filter_by(email='linkmunirih@gmail.com').first()
    user.set_password('FlaskIsAwesome123')
    database.session.add(user)
    database.session.commit()



@pytest.fixture(scope='function')
def add_stocks_for_default_user(test_client, log_in_default_user):
    # Add three stocks for the default user
    test_client.post('/add_stock', data={'stock_symbol': 'SAM',
                                         'number_of_shares': '27',
                                         'purchase_price': '301.23',
                                         'purchase_date': '2020-07-01'})
    test_client.post('/add_stock', data={'stock_symbol': 'COST',
                                         'number_of_shares': '76',
                                         'purchase_price': '14.67',
                                         'purchase_date': '2019-05-26'})
    test_client.post('/add_stock', data={'stock_symbol': 'TWTR',
                                         'number_of_shares': '146',
                                         'purchase_price': '34.56',
                                         'purchase_date': '2020-02-03'})
    return


@pytest.fixture(scope='function')
def mock_requests_get_success(monkeypatch):
    # Create a mock for the requests.get() call to prevent making the actual API call
    def mock_get(url):
        return MockSuccessResponse(url)

    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', mock_get)



@pytest.fixture(scope='function')
def mock_requests_get_api_rate_limit_exceeded(monkeypatch):
    def mock_get(url):
        return MockApiRateLimitExceededResponse(url)

    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', mock_get)



@pytest.fixture(scope='function')
def mock_requests_get_failure(monkeypatch):
    def mock_get(url):
        return MockFailedResponse(url)

    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', mock_get)


@pytest.fixture(scope='function')
def mock_requests_get_success_weekly(monkeypatch):
    # Create a mock for the requests.get() call to prevent making the actual API call
    def mock_get(url):
        return MockSuccessResponseWeekly(url)

    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', mock_get)
    

@pytest.fixture(scope='module')
def register_second_user(test_client):
    """Registers the second user using the '/users/register' route."""
    test_client.post('/users/register',
                     data={'email': 'patrick@yahoo.com',
                           'password': 'FlaskIsTheBest987'})


@pytest.fixture(scope='function')
def log_in_second_user(test_client, register_second_user):
    # Log in the user
    test_client.post('/users/login',
                     data={'email': 'patrick@yahoo.com',
                           'password': 'FlaskIsTheBest987'})

    yield   # this is where the testing happens!

    # Log out the user
    test_client.get('/users/logout', follow_redirects=True)


def test_get_stock_detail_page_failed_response(test_client, add_stocks_for_default_user, mock_requests_get_failure):
    """
    GIVEN a Flask application
    WHEN the '/stocks/3' page is retrieved (GET) when the user is logged in, but the response from Alpha Vantage failed
    THEN check that the response is valid but the chart is not displayed
    """
    response = test_client.get('/stocks/3', follow_redirects=True)
    assert response.status_code == 200
    assert b'Stock Details:' in response.data
    assert b'canvas id="stockChart"' not in response.data


def test_get_stock_detail_page_incorrect_user(test_client, log_in_second_user):
    """
    GIVEN a Flask application
    WHEN the '/stocks/3' page is retrieved (GET) by the incorrect user
    THEN check that a 403 error is returned
    """
    response = test_client.get('/stocks/3')
    assert response.status_code == 403
    assert b'Stock Details:' not in response.data
    assert b'canvas id="stockChart"' not in response.data


def test_get_stock_detail_page_invalid_stock(test_client, log_in_default_user):
    """
    GIVEN a Flask application
    WHEN the '/stocks/234' page is retrieved (GET)
    THEN check that a 404 error is returned
    """
    response = test_client.get('/stocks/234')
    assert response.status_code == 404
    assert b'Stock Details:' not in response.data