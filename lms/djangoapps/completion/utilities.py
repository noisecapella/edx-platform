# Django imports
from django.core.urlresolvers import reverse

# edX imports
from lms.djangoapps.completion.models import BlockCompletion

class UnavailableCompletionData(Exception):
    def __init__(self):
        Exception.__init__(self, "User has not completed blocks in enrollment.")

def get_url_to_last_completed_block(user, enrollment):
    '''Throws exception if LastCompletedBlock is None'''
    try:
        LastCompletedBlock = BlockCompletion.get_latest_block_completed(user, enrollment.course_id)
        urlToBlock = reverse('jump_to', kwargs={'course_id': enrollment.course_id, 'location': LastCompletedBlock.block_key})
        return urlToBlock
    except AttributeError:
        # caught when user hasn't completed anything during the enrollmment.
        raise UnavailableCompletionData