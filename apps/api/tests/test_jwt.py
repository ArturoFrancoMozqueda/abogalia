"""JWT negatives use ephemeral synthetic keys/tokens exclusively in memory."""

import json

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from abogalia_api.identity.security import InvalidToken, JWTVerifier

pytest_plugins = ["test_auth"]


@pytest.mark.parametrize(
    "overrides",
    [
        {"iss": "https://other.example.invalid/auth/v1"},
        {"aud": "another-product"},
        {"sub": "not-a-subject"},
        {"session_id": "not-a-session"},
        {"aal": "admin"},
        {"exp": 1},
        {"iat": 9999999999},
        {"exp": True},
        {"iat": "1"},
        {"exp": 9999999999},
        {"nbf": 9999999999},
    ],
)
def test_required_claims_fail_closed(rig, overrides):
    _, app, _, _, mock, clock = rig
    with pytest.raises(InvalidToken):
        app.state.identity.verifier.verify(mock.issue(**overrides), clock())


def test_jwt_signature_and_algorithm_confusion(rig):
    _, app, _, _, mock, clock = rig
    token = mock.issue()
    head, payload, signature = token.split(".")
    changed = "A" if signature[0] != "A" else "B"
    with pytest.raises(InvalidToken):
        app.state.identity.verifier.verify(
            head + "." + payload + "." + changed + signature[1:], clock()
        )
    token = jwt.encode(
        {"sub": mock.subject},
        "public-synthetic-marker" * 3,
        algorithm="HS256",
        headers={"kid": "synthetic"},
    )
    with pytest.raises(InvalidToken):
        app.state.identity.verifier.verify(token, clock())


def test_missing_claim_and_attacker_key_location(rig):
    _, app, _, _, mock, clock = rig
    token = jwt.encode(
        {"sub": mock.subject},
        mock.key,
        algorithm="ES256",
        headers={
            "kid": "synthetic",
            "jku": "https://attacker.example.invalid/key",
        },
    )
    with pytest.raises(InvalidToken):
        app.state.identity.verifier.verify(token, clock())
    token = jwt.encode(
        {"sub": mock.subject}, mock.key, algorithm="ES256", headers={"kid": "synthetic"}
    )
    with pytest.raises(InvalidToken):
        app.state.identity.verifier.verify(token, clock())


def test_rsa_only_with_matching_trusted_key(rig):
    _, app, _, _, mock, clock = rig
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key()))
    public.update(kid="rsa-synthetic", alg="RS256", use="sig")
    claims = jwt.decode(mock.issue(), options={"verify_signature": False})
    token = jwt.encode(claims, key, algorithm="RS256", headers={"kid": "rsa-synthetic"})
    verifier = JWTVerifier(app.state.identity.settings, lambda: {"keys": [public]})
    assert verifier.verify(token, clock()).subject == mock.subject


def test_cap_lifetime_rejected_before_local_session_creation(rig):
    client, _, store, _, mock, _ = rig
    from test_auth import bootstrap

    mock.token_lifetime = 901
    response = client.post(
        "/api/auth/login",
        headers=bootstrap(client),
        json={
            "email": "person@example.invalid",
            "password": "marker",
        },
    )
    assert response.status_code == 503
    assert not store.rows
