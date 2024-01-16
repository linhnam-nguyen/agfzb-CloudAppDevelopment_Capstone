import requests
import json
from datetime import datetime
# import related models here
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
# def get_request( params=None, headers=None, auth=None):
#     response = requests.get(url='http://localhost:3000/dealerships/get', params=params, headers=headers, auth=auth)
#     return response

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# def get_request(url, **kwargs):
    
#     # If argument contain API KEY
#     api_key = kwargs.get("api_key")
#     print("GET from {} ".format(url))
#     try:
#         if api_key:
#             params = dict()
#             params["text"] = kwargs["text"]
#             params["version"] = kwargs["version"]
#             params["features"] = kwargs["features"]
#             params["return_analyzed_text"] = kwargs["return_analyzed_text"]
#             response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
#         else:
#             # Call get method of requests library with URL and parameters
#             response = requests.get(url, headers={'Content-Type': 'application/json'},
#                                     params=kwargs)
#     except:
#         # If any error occurs
#         print("Network exception occurred")

#     status_code = response.status_code
#     print("With status {} ".format(status_code))
#     json_data = json.loads(response.text)
#     return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
# def post_request(json_data):
#     url= 'http://localhost:3000/dealerships/get'
#     response = requests.post(url, json=json_data, params=params, headers=headers, auth=auth)
#     return response

def post_request(url, data):
    print("POST to {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.post(url, json=data)
    except Exception as e:
        # If any error occurs
        print("Network exception occurred", e) 
    return response
# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(**kwargs):
    url= 'http://localhost:3000/dealerships/get'
    results = []
    # Call get_request with a URL parameter
    dealers = get_request(url,**kwargs)
    if dealers:
        # Get the row list in JSON as dealers
        # dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(review):
    api_url = "https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/7c06dc75-d34d-4d6c-a8e7-b53075b0c400"
    api_key = "LmXiPqrmjdLqb3h143TubskldtrjOY_0fFcYqpgKjF__"
    auth = IAMAuthenticator(api_key)
    nLU = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=auth
    )
    nLU.set_service_url(api_url)
    try: 
        resp = nLU.analyze(
            text=review,
            features=Features(sentiment=SentimentOptions(document= True))
            ).get_result()
        # label=json.dumps(resp, indent=2)
        label = resp['sentiment']['document']['label'] 
        return label
    except Exception as e:
        # Handle or log the exception as needed
        print("An error occurred:", e)
        return None, 500

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(dealerID):
    url= 'http://localhost:5000/api/get_reviews'
    responses = get_request(url,id = dealerID)
    results = []
    if responses:
        for response in responses:
            reviews_obj = DealerReview (
                dealership = response["dealership"],
                name = response["name"],
                purchase = response["purchase"],
                review = response["review"],
                purchase_date = response["purchase_date"],
                car_make = response["car_make"],
                car_model = response["car_model"],
                car_year = response["car_year"],       
                sentiment = analyze_review_sentiments(response["review"]),
                id = response["id"]
            )
            results.append(reviews_obj)
        return results
# Example usage:
# dealers = get_dealers_from_cf("https://your-cloud-function-url/dealers", city="New York")
# reviews = get_dealer_reviews_from_cf("https://your-cloud-function-url/reviews", dealerId=123)
# sentiment = analyze_review_sentiments("This is a positive review.")

def add_review(review, dealerID):
    url= 'http://localhost:5000/api/post_review'
    review_obj ={
                'dealership' : dealerID,
                'name' : review.get('name'),
                'purchase' : review.get('purchase'),
                'review' : review.get('review'),
                'purchase_date' : review.get('purchase_date'),
                'car_make' : review.get('car_make'),
                'car_model' : review.get('car_model'),
                'car_year' : review.get('car_year').isoformat(),       
                'sentiment' : analyze_review_sentiments(review.get('review')),
                'id' : review.get('id'),
                'time' : datetime.utcnow().isoformat()
    }
    # json_data=json.dumps(review_obj)
    response = post_request(url,review_obj)
    return response

