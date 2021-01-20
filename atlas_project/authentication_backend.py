from ldap3 import Server, Connection, ALL

LDAP_URL = 'ldap.forumsys.com'

# Check user authentication in the LDAP and return his information
def get_LDAP_user(username, password):
    try:
        server = Server(LDAP_URL, get_info=ALL)
        connection = Connection(server,
                                'uid={username},dc=example,dc=com'.format(
                                    username=username),
                                password, auto_bind=True)

        connection.search('dc=example,dc=com', '({attr}={login})'.format(
            attr='uid', login=username), attributes=['uid', 'mail', 'givenName', 'sn'])

        if len(connection.response) == 0:
            return None

        print(connection.response)
        print(connection.entries[0].entry_to_ldif())
        
        userd = connection.response[0]
        
        connection.search('dc=example,dc=com', '({attr}={login})'.format(
            attr='ou', login='mathematicians'), attributes=['ou', 'uniqueMember'])
        
        print(connection.response[0])
        
        return userd
    except:
        return None

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class AuthenticationBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):

        username = request.GET.get('username')
        password = request.GET.get('password')
        
        userdata = get_LDAP_user(username, password)
        
        # Get the user information from the LDAP if he can be authenticated
        if userdata is None:
            return None
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username)
            print()
            user.is_superuser = True
            user.is_staff = True
            user.set_password(password)
            try:
                user.first_name = userdata['attributes']['givenName'][0]
            except IndexError:
                user.first_name = ''
            try:
                user.last_name = userdata['attributes']['sn'][0]
            except IndexError:
                user.last_name = ''
            try:
                user.email = userdata['attributes']['mail'][0]
            except IndexError:
                user.email = ''
            user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None