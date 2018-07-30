from django.db import models


# Create your models here.
class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    @property
    def address_line_1(self):
        """Returns first address line (street)"""
        return self.street

    @property
    def address_line_2(self):
        """Returns second address line (city, state)"""
        return "%s, %s" % (self.city, self.state)

    @property
    def address_line_3(self):
        """Returns third address line (zip code, country"""
        return "%s %s" % (self.zip_code, self.country)

    def __str__(self):
        return "%s, %s, %s, %s, %s" % (self.street, self.city, self.state, self.zip_code, self.country)


class Client(models.Model):
    client_number = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Lawyer(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Matter(models.Model):
    FEE_CHOICES = ((u'Fixed', 'Fixed'), (u'Hourly', 'Hourly'))
    file_number = models.CharField(max_length=50)
    invoice_date = models.DateTimeField()
    matter_number = models.CharField(max_length=50)
    summary = models.CharField(max_length=255)
    fee_choice = models.CharField("Fixed fee or hourly?", max_length=20, choices=FEE_CHOICES)
    trust = models.DecimalField(max_digits=10, decimal_places=2)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)

    @property
    def invoice_number(self):
        """Returns the invoice number (client number - matter number"""

        return '%s-%s' % (self.client.client_number, self.matter_number)

    class Meta:
        ordering = ('invoice_date',)

    def __str__(self):
        return self.summary


class Service(models.Model):
    date = models.DateTimeField()
    description = models.CharField(max_length=255)
    hours = models.IntegerField(default=1, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE)
    matter = models.ForeignKey(Matter, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ('date',)

    def __str__(self):
        return self.description


class Disbursement(models.Model):
    TAX_CHOICES = ((u'Taxable', 'Taxable'), (u'Non-Taxable', 'Non-Taxable'))
    date = models.DateTimeField()
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_choice = models.CharField("Taxable/Non-Taxable", max_length=20, choices=TAX_CHOICES)
    matter = models.ForeignKey(Matter, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ('date',)

    def __str__(self):
        return self.description


class Discount(models.Model):
    DISCOUNT_CHOICES = ((u'Percentage', 'Percentage'), (u'Flat', 'Flat'))
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount_choice = models.CharField("Percentage of Flat?", max_length=20, choices=DISCOUNT_CHOICES)
    matter = models.ForeignKey(Matter, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)

    def __str__(self):
        if self.discount_choice == 'Flat':
            return '${}-{}'.format(self.amount, self.name)
        return '{}%-{}'.format(self.amount, self.name)


