from django.shortcuts import render

from rest_framework import viewsets, request, response, renderers
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import detail_route
from rest_framework.decorators import api_view, renderer_classes, \
    permission_classes
from rest_framework.renderers import TemplateHTMLRenderer

from generank.reporting.tasks import *

@api_view(['GET'])
@permission_classes([IsAdminUser])
@renderer_classes((TemplateHTMLRenderer,))
def report(request):
    ''' This returns all the report page for MyGeneRank '''

    # Numerical Data
    num_users, num_recent_users = get_user_info()
    perc_import, perc_follow = get_usage_info()
    perc_risk_score_complete = get_risk_score_status_info()

    # Graphs
    user_growth_graph = plot_users()
    risk_score_graph = plot_risk_scores()

    data = {'num_users':num_users,
            'num_recent_users':num_recent_users,
            'perc_import': perc_import,
            'perc_follow': perc_follow,
            'perc_risk_score_complete': perc_risk_score_complete,
            'risk_score_graph': risk_score_graph,
            'user_growth_graph': user_growth_graph}

    return response.Response(data, template_name='reports.html')
