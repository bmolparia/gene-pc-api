import base64
from io import BytesIO
from datetime import datetime, timedelta, timezone
from collections import Counter

import numpy as np

import matplotlib as mp
mp.use('Agg')
from matplotlib import pyplot as plt

from celery import shared_task

from django.conf import settings
from generank.api.models import User, Activity, ActivityStatus, RiskScore, \
                            Population, Condition


@shared_task
def get_user_info():
    ''' Returns the total users and new users in the past 24 hours '''

    number_users = User.objects.filter(is_active=True).count()

    now = datetime.now(timezone.utc)
    one_day = now - timedelta(days=1)
    number_recent_users = User.objects.filter(date_joined__date__gt = one_day,
                                       is_active=True).count()

    return number_users, number_recent_users

@shared_task
def get_usage_info():
    ''' Percentage of people who have imported their data and the
    Percentage of people who have completed follow ups. '''

    ttm_login = settings.GENOTYPE_AUTH_SURVEY_ID
    cad_suvery = settings.POST_CAD_RESULTS_SURVEY_ID

    active_users = User.objects.filter(is_active=True)
    number_users = User.objects.filter(is_active=True).count()

    import_activity = Activity.objects.filter(study_task_identifier=ttm_login)
    import_done = ActivityStatus.objects.filter(user__in = active_users,
                                            activity = import_activity,
                                            complete = True).count()

    follow_activity = Activity.objects.filter(study_task_identifier=cad_suvery)
    follow_done = ActivityStatus.objects.filter(user__in = active_users,
                                            activity = follow_activity,
                                            complete = True).count()

    perc_import = round(100*(import_done/float(number_users)),2)
    perc_follow = round(100*(follow_done/float(number_users)),2)

    return perc_import, perc_follow

@shared_task
def get_risk_score_status_info():
    ''' Percentage of people who have received their score and have imported
    their data. '''

    active_users = User.objects.filter(is_active=True)
    population = Population.objects.filter(name__exact='custom')
    all_risk_scores_complete = RiskScore.objects.filter(user__in = active_users,
                                            population__in = population,
                                            calculated = True).count()
    num_users = float(len(active_users))
    perc_risk_score_complete = round(100*(all_risk_scores_complete/num_users),2)

    return perc_risk_score_complete

@shared_task
def get_risk_scores(condition):
    ''' Returns a list of the last 200 risk scores. Segregate by condition. '''

    active_users = User.objects.filter(is_active=True)
    population = Population.objects.filter(name__exact='custom')
    last_200_risk_scores = RiskScore.objects.filter(user__in = active_users,
                            population__in = population,
                            calculated = True,
                            condition = condition).order_by('created_on')[:200]

    last_200_risk_score_values = [(100*x.value) for x in last_200_risk_scores]

    return last_200_risk_score_values

@shared_task
def plot_users():
    ''' Makers a plot of the number of users over time and returns the byte
    string for the plot '''

    active_users = User.objects.filter(is_active=True).order_by('date_joined')

    # Query all the dates when users joined and change the day to 1
    dates = [datetime(year=x.date_joined.year, month=x.date_joined.month,
                                                   day=1) for x in active_users]

    user_distribution = Counter(dates)
    dates_graph = sorted(list(user_distribution))
    users_overtime = [user_distribution[x] for x in dates_graph]
    users_cumsum = np.cumsum(users_overtime)

    # Plotting
    fig = plt.figure(figsize=(8,5))
    plt.plot(dates_graph,users_overtime,color='steelblue',label = 'Per Month')
    plt.plot(dates_graph,users_cumsum,color='DarkOrange',label = 'Cumulative')
    plt.ylabel('Number of Users')
    plt.xlabel('Date')
    plt.title('User Growth')

    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    buf = BytesIO()
    plt.savefig(buf,format='png',bbox_inches='tight')
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()
    plt.close()

    return image_base64

@shared_task
def plot_risk_scores():
    ''' Makes a scatter plot of the risk scores and returns the byte string
    for the plot '''

    conditions = list(Condition.objects.all())
    num_condtions = len(conditions)

    w,h = 8,3*num_condtions
    fig, axes_arr = plt.subplots(num_condtions, sharex=True,figsize=(w,h))
    for condition in conditions:

        plot_num = conditions.index(condition)
        risk_scores = get_risk_scores(condition)
        current_axis = axes_arr[plot_num]

        # Plotting
        current_axis.plot(risk_scores,'o',color='steelblue', label = 'Risk Score')
        current_axis.set_title(condition.name)
        current_axis.set_ylabel('Percentile')
        current_axis.set_ylim(0, 100)
        # Remove the x axis ticks
        current_axis.tick_params(axis='x', which='both', bottom='off',
        top='off',labelbottom='off')

        current_axis.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    plt.suptitle('Last 200 Risk Score Distribution')
    plt.subplots_adjust(top=0.85)

    buf = BytesIO()
    plt.savefig(buf,format='png',bbox_inches='tight')
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()
    plt.close()

    return image_base64
