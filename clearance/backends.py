import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_clearance.settings')

from django.contrib.auth.hashers import check_password
password = 'your_password'
encoded_hash = 'pbkdf2_sha256$600000$2KGx5Jx2OwEL35q9w7b1xX$p6pb+3fIzF+mTvZnvOQBTJMGD46kwLkUnU07SSWzcuk='

result = check_password(password, encoded_hash)
print(result)
