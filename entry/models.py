from django.db import models
from django.core.validators import EmailValidator, MaxValueValidator, MinLengthValidator, MinValueValidator
from django.contrib.auth.models import User


class Employee(models.Model):  # the user model includes the admin, employee and security guard
    mobile = models.CharField(max_length=10)  # mobile no for registration
    pic = models.ImageField(upload_to='media')  # photo of the user
    admin = models.BooleanField(default=False)  # admin status availability
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Visitor(models.Model):
    name = models.CharField(max_length=200, validators=[
        MinLengthValidator(2, 'Minimum 2 Characters are required')])  # name of the visitor
    purpose = models.CharField(max_length=200, validators=[
        MinLengthValidator(4, 'Minimum 4 characters are required')])  # purpose of visit
    mobile = models.IntegerField()  # mobile no. of the visitor
    email = models.EmailField(validators=[EmailValidator()])  # email address of the visitor
    no_of_people = models.IntegerField()  # no. of visitors
    in_time = models.DateTimeField(auto_now_add=False)  # in time of the visitor, added automatically
    out_time = models.DateTimeField(auto_now=True)  # out time of the visitor added automatically
    employee_to_visit = models.CharField(max_length=200)  # enter the employee whom the visitor is visiting
    token = models.CharField(max_length=200)  # token(autogenerated)
    qrcode = models.ImageField(upload_to='media/qrcodes')  # qr code generated from the token
    user = models.ForeignKey(Employee,
                             on_delete=models.PROTECT)  # link to the User table, to store which user allowed the entry
    
    def __str__(self):
        return self.name
