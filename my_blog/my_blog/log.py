from my_blog.settings import LOGGING
import logging
from django.http import HttpResponse


logging.config.dictConfig(LOGGING)
logger = logging.getLogger('django.request')

def whatever(request):
    # do something
    logger.warning('Something went wrong!')
    # do something else
    return HttpResponse('Whatever function executed successfully!')