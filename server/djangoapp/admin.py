from django.contrib import admin
# from .models import related models
from .models import CarModel, CarMake

# Register your models here.

# CarModelInline class
class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 5

# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'carmake_display', 'type', 'year']
    # fields =['get_name', 'get_carmake','get_type', 'get_year', 'get_dealerID']
    fields =['name', 'carmake', 'type', 'year', 'dealerID']

    # def get_name(self, obj):
    #     return obj.name
    # get_name.short_description = 'Model'   

    # def get_carmake(self, obj):
    #     return obj.carmake
    # get_carmake.short_description = 'Refered Lesson'
    
    # def get_type(self, obj):
    #     return obj.type
    # get_type.short_description = 'Type'
    
    # def get_year(self, obj):
    #     return obj.lesson
    # get_year.short_description = 'Year'

    # def get_dealerID(self, obj):
    #     return obj.dealerID
    # get_dealerID.short_description = 'Dealer ID'
    
    def carmake_display(self, obj):
            return obj.carmake.name
    carmake_display.short_description = 'Fabrication'
    # def dealer_display(self, obj):
    #         return obj.dealerID.short_name
    # dealer_display.short_description = 'Dealer'
    
    
# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    list_display = ['name', 'description']
    search_fields = ['name', 'description']
# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)
