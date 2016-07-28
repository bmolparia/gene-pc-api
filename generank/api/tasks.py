from __future__ import absolute_import

from celery import shared_task
from celery.utils.log import get_task_logger

from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist

from push_notifications.models import APNSDevice

from .models import User, Activity, ActivityStatus, RiskScore


logger = get_task_logger(__name__)


@shared_task
def send_registration_email_to_user(registration_url, registration_code, user_email):
    html = render_to_string('registration_email.html', {
        'url': registration_url,
        'code': registration_code
    })
    logger.info('Sending email to new user: %s' % user_email)
    send_mail(settings.REGISTER_EMAIL_SUBJECT, '', settings.EMAIL_HOST_USER,
        [user_email], fail_silently=False, html_message=html)


@shared_task
def send_risk_score_notification(user_id, condition_name):
    try:
        device = APNSDevice.objects.get(user__id=user_id)
        device.send("Your risk score for {condition} is available.".format(
            condition=condition_name))
        logger.info('Notification sent to user for new risk score: '
            'User <%s> | Condition <%s>' % (user_id, condition_name))
    except ObjectDoesNotExist:
        logger.warning("Device for user %s does not exist." % user_id)


@shared_task
def send_activity_notification(activity_id):
    activity = Activity.objects.get(id=activity_id)
    # TODO: refactor to use mass_send
    devices = APNSDevice.objects.filter(active=True)
    devices.send_message('A new activity is ready for you!')
    logger.info('New mass activity notification sent to all users.')


@shared_task
def create_statuses_for_existing_users(activity_id):
    activity = Activity.objects.get(id=activity_id)
    for user in User.objects.all():
        status = ActivityStatus(user=user, activity=activity)
        status.save()
    logger.info('New statuses created for existing users.')


@shared_task
def create_statuses_for_new_user(user_id):
    user = User.objects.get(id=user_id)
    for activity in Activity.objects.all():
        status = ActivityStatus(user=user, activity=activity)
        status.save()
    logger.info('New statuses created for new user: %s' % user_id)