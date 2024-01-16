from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    # route is a string contains a URL pattern
    # view refers to the view function
    # name the URL

    # path for about view
    path(route='about/', view=views.about, name='about_us'),

    # path for contact us view
    path(route='contact/', view=views.contact, name='contact_us'),
    # path for registration
    path(route='registration/', view=views.registration_request, name='registration'),
    # path for login
    path(route='login/', view=views.login_request, name='login'),
    # path for logout
    path(route='logout/', view=views.logout_request, name='logout'),
    
    path(route='', view=views.CarDealerListView.as_view(), name='index'),

    # path for dealer reviews view
    path(route='dealer/<int:dealer_id>', view=views.CarDealerDetailView.as_view(), name='dealer_details'),
    
    # path for add a review view
    path(route ='review_form/<int:dealer_id>', view=views.review_form, name='review'),
    path(route ='add_review/<int:dealer_id>',view=views.get_dealer_details,name ='add_review')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)