from typing import Annotated

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError

from src.config import config

JWKS_URL = f"{config['auth0_domain']}/.well-known/jwks.json"

# Get and cache jwks from auth0
with httpx.Client() as client:
    response = client.get(JWKS_URL)
    jwks_cache = response.json()

http_bearer = HTTPBearer(scheme_name="Bearer")


def auth(http_bearer: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]):
    """Dependency that validates bearer token and returns user's subject.
    https://auth0.com/docs/quickstart/backend/python/01-authorization"""
    oauth_token = http_bearer.credentials
    jwks = jwks_cache

    try:
        unverified_header = jwt.get_unverified_header(oauth_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not get unverified header")
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                oauth_token,
                rsa_key,
                algorithms=config["auth0_algorithms"],
                audience=config["auth0_api_audience"],
                issuer=f"{config['auth0_domain']}/",
            )
            return payload["sub"]
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token is expired")
        except JWTClaimsError:
            raise HTTPException(
                status_code=401,
                detail="Incorrect claims, please check the audience and issuer",
            )
        except JWTError:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )
    raise HTTPException(
        status_code=401, detail="Unable to find appropriate key for JWT"
    )
