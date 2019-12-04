from dataclasses import dataclass

from django.conf import settings
from passlib.apache import HtpasswdFile
from rest_framework import exceptions
from rest_framework.authentication import (
    BasicAuthentication, TokenAuthentication
)


@dataclass
class DummyUser:
    """Dummy class to simulate real User to add to request"""
    username: str
    is_authenticated: bool = True


class OwnBasicAuthentication(BasicAuthentication):
    """
    Changed default HTTP Basic authentication against username/password.
    Usernames and passwords hashes are stored in .htpasswd file
    """
    def authenticate_credentials(self, userid, password, request=None):
        ht = HtpasswdFile(settings.PATH_TO_HTPASSWD_FILE)
        result = ht.check_password(userid, password)
        usernames = ht.users()

        if result is None:
            raise exceptions.AuthenticationFailed('Invalid username.')
        elif not result:
            raise exceptions.AuthenticationFailed('Invalid password.')
        else:
            if userid == usernames[0]:
                return (self.get_user('admin'), None)
            else:
                return (self.get_user(userid), None)

    def get_user(self, username):
        return DummyUser(username=username)


class OwnTokenAuthentication(TokenAuthentication):
    """
    Token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a

    Usernames and passwords hashes are stored in .htpasswd file
    """
    def authenticate_credentials(self, key):
        ht = HtpasswdFile(settings.PATH_TO_HTPASSWD_FILE)

        usernames = ht.users()
        for username in usernames:
            check_result = ht.check_password(username, key)
            if check_result:
                if username == usernames[0]:
                    return (self.get_user('admin'), key)
                else:
                    return (self.get_user(username), key)

        raise exceptions.AuthenticationFailed('Invalid token.')

    def get_user(self, username):
        return DummyUser(username=username)
