'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.shortcuts import (
    redirect, 
    render
)

from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required


################################################################################
# AUTHENTICATION
################################################################################


def validate_credentials(user, context=None):
    '''validate_credentials will return a context object with "aok" for each credential
       that exists, and "None" if it does not for a given user
 
       Parameters
       ==========
       user: the user to check, should have social_auth
       context: an optional context object to append to
    '''
    if context is None:
        context = dict()

    # Right now we have github for repos and google for storage
    credentials = [{'provider':'google-oauth2', 'key':'google_credentials'},
                   {'provider':'github', 'key':'github_credentials'},
                   {'provider':'globus', 'key':'globus_credentials'},
                   {'provider':'twitter', 'key':'twitter_credentials'}] 

    # Iterate through credentials, and set each available to aok. This is how
    # the templates will know to tell users which they need to add, etc.
    credentials_missing = "aok"
    for group in credentials:
        credential = None
        if not user.is_anonymous:
            credential = user.get_credentials(provider=group['provider'])
        if credential is not None:
            context[group['key']] = 'aok'
        else:
            credentials_missing = None

    # This is a global variable to indicate all credentials good
    context['credentials'] = credentials_missing
    return context


def agree_terms(request):
    '''ajax view for the user to agree'''
    if request.method == 'POST':
        request.user.agree_terms = True
        request.user.agree_terms_date = timezone.now()
        request.user.save()
        response_data = {'status': request.user.agree_terms}
        return JsonResponse(response_data)

    return JsonResponse({"Unicorn poop cookies...": "I will never understand the allure."})



def login(request, message=None):
    '''login will either show the user a button to login with github, and then a link
       to their collections (given storage is set up) or a link to connect storage (if it 
       isn't)
    '''
    if message is not None:
        messages.info(request, message)    

    context = None
    if request.user.is_authenticated:
        if not request.user.agree_terms:
            return render(request, 'terms/usage_agreement_login.html', context)
        context = validate_credentials(user=request.user)
    return render(request, 'social/login.html', context)


@login_required
def logout(request):
    '''log the user out, first trying to remove the user_id in the request session
    skip if it doesn't exist
    '''
    try:
        del request.session['user_id']
    except KeyError:
        pass
    auth_logout(request)

    return redirect('/')



#######################################################################################
# SOCIAL AUTH
#######################################################################################

def redirect_if_no_refresh_token(backend, response, social, *args, **kwargs):
    '''http://python-social-auth.readthedocs.io/en/latest/use_cases.html#re-prompt-google-oauth2-users-to-refresh-the-refresh-token
    '''
    if backend.name == 'google-oauth2' and social and response.get('refresh_token') is None and social.extra_data.get('refresh_token') is None:
        return redirect('/login/google-oauth2?approval_prompt=force')


## Ensure equivalent email across accounts

def social_user(backend, uid, user=None, *args, **kwargs):
    '''OVERRIDED: It will give the user an error message if the
       account is already associated with a username.'''
    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)

    if social:
        if user and social.user != user:
            msg = 'This {0} account is already in use.'.format(provider)
            return login(request=backend.strategy.request, message=msg)
            #raise AuthAlreadyAssociated(backend, msg)
        elif not user:
            user = social.user

    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': social is None}
