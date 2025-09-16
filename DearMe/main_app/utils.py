from django.core.signing import TimestampSigner, SignatureExpired, BadSignature

signer = TimestampSigner()

def generate_email_token(user_id):
    return(signer.sign(user_id))

def verify_email_token(token, max_age=60*60*24):
    try:
        user_id = signer.unsign(token,max_age=max_age)
        return int(user_id)
    except(SignatureExpired, BadSignature):
        return None