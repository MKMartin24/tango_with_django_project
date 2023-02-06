from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from rango.models import Category,Page

def index(request):

    #Query the db for a list of ALL categories currently stored.
    #Order the categories by th number oflikes in descending order
    #Retrieve the top 5 only -- or all if less than 5 pages
    #Place the list in our Ontext_dict (with our boldmessage)
    #that will be passed to the template engine

    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = pages_list
    
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    context_dict = {'boldmessage': 'MKMartin24'}
    return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
    #Create a context dictionary which we can pass
    #to the template rendering machine
    context_dict = {}

    try:
        #Can we find a category name slug with the given name?
        #If we can't, the .get() raises a DoesNotExist exception.
        #The .get() method returns on emodel instance or raises an exception
        category = Category.objects.get(slug = category_name_slug)

        #Retrieve all of associated pages.
        #The filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category)

        #Add our results list to the template context under name pages.
        context_dict['pages'] = pages
        #We also add the category object from hte database to the context_dictionary
        #We'll use this in the template to verify that the category exists
        context_dict['category'] = category
    except Category.DoesNotExist:
        #We get here if we didn't find the specified category.
        #Don't do anything -
        #the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None
    
    #Go render the response and return it to the client.
    return render(request, 'rango/category.html', context=context_dict)