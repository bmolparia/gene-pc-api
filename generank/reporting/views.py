from datetime import datetime, timedelta, timezone

from django.shortcuts import render

from rest_framework import viewsets, request, response, renderers
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import detail_route
from rest_framework.decorators import api_view, renderer_classes, \
    permission_classes
from rest_framework.renderers import TemplateHTMLRenderer

from generank.api.models import User

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAdminUser])
@renderer_classes((TemplateHTMLRenderer,))
def report(request):
    ''' This returns all the data required for plotting the charts '''

    num_users, num_recent_users = user_info()

    data = {'num_users':num_users,
            'num_recent_users':num_recent_users}

    return response.Response(data, template_name='reports.html')

def user_info():
    ''' Returns the total users and new users in the past 24 hours '''
    all_users = User.objects.all()
    number_users = len(all_users)

    now = datetime.now(timezone.utc)
    one_day = now - timedelta(days=1)
    recent_users = User.objects.filter(date_joined__date__gt = one_day)
    number_recent_users = len(recent_users)

    return number_users, number_recent_users

def usage_info():
    ''' Percentage of people who have imported their data and the
    Percentage of people who have completed follow ups. '''

    return ()

def app_well_being_info():
    ''' Percentage of people who have received their score and have imported
    their data. '''
    return ()

def risk_scores():
    ''' Returns a list of the last 200 risk scores. Segregate by condition. '''
    return ()
