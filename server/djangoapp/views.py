from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.http import HttpResponse as HttpResponse, HttpRequest, HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarModel
# from django.views.decorators.csrf import csrf_exempt
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, add_review
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.generic import TemplateView, DetailView
from datetime import datetime
from django.urls import reverse
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
#def contact(request):
# Create an `about` view to render a static about page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)
    
# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('psw')
        current_template = request.POST.get('current_template')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['login_failed'] = 'true'
            return render(request, 'djangoapp/'+current_template, context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
# def get_dealerships(request):
#         # Accessing the session ID
#     session_id = request.session.session_key
#     print(session_id)
#     if not session_id:
#         # If the session ID doesn't exist, Django will create one
#         request.session.save()
#         session_id = request.session.session_key

        
#     if request.method == "GET":
#         # Get dealers from the URL
#         dealerships = get_dealers_from_cf()
#         # Concat all dealer's short name
#         # Return a list of dealer short name
#         return dealerships

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
# @csrf_exempt
def get_dealer_details(request,dealer_id):
        # Accessing the session ID
    session_id = request.session.session_key
    print(session_id)
    if not session_id:
        # If the session ID doesn't exist, Django will create one
        request.session.save()
        session_id = request.session.session_key
    if request.method == "GET":
        reviews= get_dealer_reviews_from_cf(dealer_id)
        return reviews
    
    print(request)
    if request.method == "POST":
        post_data = request.POST.copy()
        car_model = get_object_or_404(CarModel,id=request.POST.get('car_id'))
        post_data["car_make"] = car_model.carmake.name
        post_data["car_model"] = car_model.name
        post_data["car_year"] = car_model.year
        post_data["purchase"] = "true" if request.POST.get('purchase') == "on" else "false"
        post_data["id"] = dealer_id
        try: 
            review= add_review(post_data, dealer_id)
        except Exception as e:
        # If any error occurs
            print("Network exception occurred", e) 
        return HttpResponseRedirect(reverse(viewname='djangoapp:dealer_details', args=(dealer_id,)))

class CarDealerDetailView(TemplateView):
    template_name = 'djangoapp/dealer_details.html'

    def get_context_data(self, **kwargs):
        # First, call the base implementation to get a context
        context = super().get_context_data(**kwargs)

        # Get dealer_id from the URL parameters
        dealer_id = self.kwargs['dealer_id']

        # Get reviews using the get_dealer_details function
        reviews = get_dealer_details(self.request, dealer_id)

        # Add reviews to the context
        context['dealer_id']= dealer_id
        context['reviews_list'] = reviews

        return context
    
class CarDealerListView(TemplateView):
            # Accessing the session ID
    template_name = 'djangoapp/index.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        # Accessing the session ID
        session_id = self.request.session.session_key
        print(session_id)
        if not session_id:
            # If the session ID doesn't exist, Django will create one
            self.request.session.save()
            session_id = self.request.session.session_key
        
        dealers_data = get_dealers_from_cf()
        context['dealership_list'] = dealers_data
        return context

def review_form(request, dealer_id):
    
     # Fetch dealer information
    dealer = get_dealers_from_cf(id=dealer_id)

    # Fetch car models associated with the dealer
    car_models = CarModel.objects.filter(dealerID=int(dealer_id))

    # Prepare the context
    context = {
        'dealer_id': int(dealer_id),
        'dealer_name': dealer[0].full_name,
        'car_models': car_models,
    }

    return render(request, 'djangoapp/add_review.html', context)

    
        

