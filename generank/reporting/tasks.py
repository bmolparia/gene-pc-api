from datetime import datetime, timedelta, timezone
import base64
from io import BytesIO

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

from celery import shared_task

from django.conf import settings
from generank.api.models import User, Activity, ActivityStatus, RiskScore


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
                                            activity=import_activity).count()

    follow_activity = Activity.objects.filter(study_task_identifier=cad_suvery)
    follow_done = ActivityStatus.objects.filter(user__in = active_users,
                                            activity=follow_activity).count()

    perc_import = round(100*(import_done/float(number_users)),2)
    perc_follow = round(100*(follow_done/float(number_users)),2)

    return perc_import, perc_follow

@shared_task
def get_risk_score_status_info():
    ''' Percentage of people who have received their score and have imported
    their data. '''

    active_users = User.objects.filter(is_active=True)
    all_risk_scores_complete = RiskScore.objects.filter(user__in = active_users,
                                            calculated = True).count()
    num_users = float(len(active_users))
    perc_risk_score_complete = round(100*(all_risk_scores_complete/num_users),2)

    return perc_risk_score_complete

@shared_task
def get_risk_scores():
    ''' Returns a list of the last 200 risk scores. Segregate by condition. '''

    active_users = User.objects.filter(is_active=True)
    last_200_risk_scores = RiskScore.objects.filter(user__in = active_users,
                            calculated = True).order_by('created_on')[:200]
    last_200_risk_score_values = [x.value for x in last_200_risk_scores]

    return last_200_risk_score_values

@shared_task
def plot_risk_scores(risk_scores):
    ''' Makes a scatter plot of the risk scores and returns the byte string
    for the plot '''

    plt.plot(risk_scores,'o',color='steelblue')
    plt.ylim(0, 100)
    plt.tick_params(axis='x', which='both', bottom='off',top='off',
     labelbottom='off')
    plt.title('Risk Scores')

    buf = BytesIO()
    plt.savefig(buf,format='png')
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()

    return image_base64
