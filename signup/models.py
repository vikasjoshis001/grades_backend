from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password

# Create your models here.


class Signup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    reg_no = models.CharField(max_length=20, unique=True)
    email = models.EmailField(validators=[RegexValidator(r'^.+@sggs\.ac\.in$',
                                                         'Email must end with @sggs.ac.in')], unique=True)
    department = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, unique=True)
    joining_year = models.PositiveIntegerField()
    course = models.CharField(max_length=100)
    password = models.CharField(max_length=128)
    status = models.CharField(max_length=50, blank=True)

    def save(self, *args, **kwargs):
        # Hash the password before saving
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
      return self.reg_no
