from django.contrib import admin
from .models import Address, Client, Lawyer, Matter, Service, Disbursement, Discount

# Register your models here.

admin.site.register(Address)
admin.site.register(Client)
admin.site.register(Lawyer)
admin.site.register(Matter)
admin.site.register(Service)
admin.site.register(Discount)
admin.site.register(Disbursement)
