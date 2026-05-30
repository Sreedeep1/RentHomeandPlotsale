from django.db import models

class tbl_login(models.Model):
    email=models.EmailField(max_length=100)
    password=models.CharField(max_length=25)
    userrole=models.CharField(max_length=25)
    def __str__(self):
        return self.email
class tbl_user(models.Model):
    login=models.ForeignKey(tbl_login,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    phone=models.CharField(max_length=10)
    created_at=models.DateField(auto_now=True)
    status=models.CharField(max_length=15,default='Active')
