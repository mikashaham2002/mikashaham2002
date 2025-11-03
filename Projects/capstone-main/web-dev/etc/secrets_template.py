# To generate secret key, use the following command:
# python -c "from django.core.management.utils import get_random_secret_key; import base64; print(base64.b64encode(get_random_secret_key().encode()).decode())"

# Secret keys are base64 encoded

from web_project.deployed_check import is_deployed

if is_deployed():
    SECRET_KEY = "PROD_SECRET_KEY"
else:
    SECRET_KEY = "DEV_SECRET_KEY"
