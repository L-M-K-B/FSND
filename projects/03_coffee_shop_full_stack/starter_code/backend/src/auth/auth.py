import json
from flask import request, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = 'coffee-shop-lb.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'dev'


# AuthError Exception: standardized way to communicate auth failure modes

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    # get the header from the request
    auth = request.headers.get('Authorization', None)
    # raise an AuthError if no header is present
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    # split bearer and the token
    parts = auth.split(' ')
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    # raise an AuthError if the header is malformed
    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    # return the token part of the header
    token = parts[1]
    return token


# TODO: check your RBAC settings in Auth0

def check_permissions(permission, payload):
    # raise an AuthError if permissions are not included in the payload
    if 'permissions' not in payload:
        abort(400)

    # raise an AuthError if the requested permission string is not in the
    # payload permissions array
    if permission not in payload['permission']:
        abort(403)

    # return true otherwise
    return True


# !!NOTE urlopen has a common certificate error described here:
# https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org

def verify_decode_jwt(token):
    # verify the token using Auth0 /.well-known/jwks.json
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    # check whether token is an Auth0 token with key id (kid)
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            # decode the payload from the token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            # return the decoded payload
            return payload

        # validate the claims
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # get the token
            token = get_token_auth_header()

            try:
                # decode the jwt
                payload = verify_decode_jwt(token)
            except:
                abort(401)

            # validate claims and check the requested permission
            check_permissions(permission, payload)

            # return the decorator which passes the decoded payload to the decorated method
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
