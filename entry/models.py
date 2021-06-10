from django.db import models
from django.core.validators import RegexValidator, EmailValidator, MinLengthValidator, MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User




class Visitor(models.Model):
	phonereg = RegexValidator(regex=r'^([0|\+[0-9]{1,5})?([0-9]{10})$')
	name = models.CharField(verbose_name='Name', max_length=200, validators=[
		MinLengthValidator(2, 'Minimum 2 Characters are required')])  # name of the visitor
	purpose = models.CharField(verbose_name='Purpose', max_length=200, validators=[
		MinLengthValidator(4, 'Minimum 4 characters are required')])  # purpose of visit
	mobile = models.CharField(validators=[phonereg], max_length=15)  # mobile no. of the visitor
	email = models.EmailField(verbose_name='Email', validators=[EmailValidator()])  # email address of the visitor
	no_of_people = models.IntegerField(verbose_name='No of people')  # no. of visitors
	actual_visitors = models.IntegerField(verbose_name='Actual No. of Visitors', null=True, blank=True) # actual no of visitors visiting
	expected_in_time = models.DateTimeField(verbose_name='Expected Visit In Time', null=True, blank=True)
	in_time = models.DateTimeField(verbose_name='Visit In time', null=True, blank=True)  # in time of the visitor, added automatically
	out_time = models.DateTimeField(verbose_name='Visit Out Time', null=True, blank=True)  # out time of the visitor added automatically
	token = models.CharField(verbose_name='Token', max_length=200, null=True, blank=True)  # token(autogenerated)
	user = models.ForeignKey(User, verbose_name='Employee to visit', on_delete=models.PROTECT)  # link to the User table, to store which user allowed the entry
	session_expired = models.BooleanField(default=False)
	
	def __str__(self):
		return self.name

class VisitorsDetail(models.Model):
	name = models.CharField(verbose_name='Name', max_length=200)
	email = models.EmailField(verbose_name='E-mail', validators=[EmailValidator()])
	safety_training = models.BooleanField(verbose_name='Is Safety Training Given?', blank=False)
	photo = models.ImageField(verbose_name='Photo of the Visitor', upload_to='media/photo', null=True, blank=True)
	mobile = models.BigIntegerField(verbose_name='Photo Id Number', blank=False, null=True, validators=[MinValueValidator(1000000000), MaxValueValidator(9999999999)])
	photo_id = models.ImageField(verbose_name='Photo Id', upload_to='media/photo_id', null=True, blank=True)
	in_time = models.DateTimeField(verbose_name="Visitor In Time", null=True, blank=True)
	out_time = models.DateTimeField(verbose_name="Visitor Out Time", null=True, blank=True)
	token = models.CharField(verbose_name='Token', max_length=200, null=True, blank=True)
	visitor = models.ForeignKey(Visitor, verbose_name='Visitor:', on_delete=models.PROTECT)
	
	def __str__(self):
		return self.name
