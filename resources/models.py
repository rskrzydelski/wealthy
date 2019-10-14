from django.db import models
from django.db.models import Sum
from accounts.models import InvestorUser

from djmoney.models.fields import MoneyField


# [singleton] market prices of resources must be only one
class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class MarketPrices(SingletonModel):
    """
    This class can have only one instance. Market price should be unique and it will be fetch from web server
    """
    gold_price = MoneyField(max_digits=10, decimal_places=2, null=True, default=6300, default_currency='PLN')
    silver_price = MoneyField(max_digits=10, decimal_places=2, null=True, default=88, default_currency='PLN')
    palladium_price = MoneyField(max_digits=10, decimal_places=2, null=True, default=5500, default_currency='PLN')
    platinum_price = MoneyField(max_digits=10, decimal_places=2, null=True, default=4500, default_currency='PLN')

    @property
    def au_sell_rate(self):
        return 0.95 * self.gold_price

    @property
    def ag_sell_rate(self):
        return 0.92 * self.silver_price

    @property
    def gold_silver_ratio(self):
        return self.gold_price / self.silver_price

    def __str__(self):
        return 'MarketPrice singleton'


# data model common for all resources
class Resource(models.Model):
    """
    Common data for resource to buy
    """
    CURRENCY_CHOICES = [('USD', 'USD $'), ('EUR', 'EUR €'), ('PLN', 'PLN ZŁ'), ('CHF', 'CHF +')]
    owner = models.ForeignKey(InvestorUser, on_delete=models.CASCADE, default=1)
    bought_price = MoneyField(max_digits=10,
                              decimal_places=2,
                              null=True,
                              blank=True,
                              currency_choices=CURRENCY_CHOICES,
                              default_currency=('PLN', 'PLN ZŁ'))
    date_of_bought = models.DateTimeField(auto_now_add=False)

    class Meta:
        abstract = True


class MetalManager(models.Manager):
    def get_metal_list(self, owner=None, name='Ag'):
        return super(MetalManager, self).filter(owner=owner, name=name)

    def get_total_gold(self, owner=None, unit='oz'):
        total = super(MetalManager, self).filter(owner=owner, name='Au', unit=unit).aggregate(amount=Sum('amount'))
        return total['amount'] or 0

    def get_total_silver(self, owner=None, unit='oz'):
        total = super(MetalManager, self).filter(owner=owner, name='Ag', unit=unit).aggregate(amount=Sum('amount'))
        return total['amount'] or 0


# data model common for all metals
class Metal(Resource):
    """
    Precious metals data
    """
    objects = MetalManager()

    METAL_CHOICES = [
        ('Ag', 'Silver'),
        ('Au', 'Gold'),
    ]
    UNIT_CHOICES = [
        ('oz', 'ounce'),
        ('g', 'gram'),
        ('kg', 'kilogram'),
    ]
    name = models.CharField(
        max_length=10,
        choices=METAL_CHOICES,
        default='Ag',
    )
    unit = models.CharField(max_length=10,
                            choices=UNIT_CHOICES,
                            default='oz')

    amount = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    description = models.TextField(blank=True, help_text='Type some information about this transaction (optional)')

    def __str__(self):
        return self.get_name_display()


class Currency(Resource):
    bought_currency = MoneyField(max_digits=10,
                                 decimal_places=2,
                                 null=True,
                                 blank=True,
                                 currency_choices=Resource.CURRENCY_CHOICES,
                                 default_currency=('CHF', 'CHF +'))

    @classmethod
    def get_currency_list(cls, owner, currency):
        return cls.objects.filter(owner=owner, bought_currency_currency__icontains=currency)

    @classmethod
    def get_total_currency(cls, owner=None, currency='CHF'):
        total_currency = cls.objects.filter(owner=owner,
                                            bought_currency_currency__icontains=currency)\
                                            .aggregate(bought_currency=Sum('bought_currency'))
        return total_currency['bought_currency']

    def __str__(self):
        return 'Currency'


class Cash(models.Model):
    owner = models.ForeignKey(InvestorUser, on_delete=models.CASCADE, default=1)
    save_date = models.DateTimeField(auto_now_add=False)
    my_cash = MoneyField(max_digits=10,
                         decimal_places=2,
                         null=True, blank=True,
                         currency_choices=Resource.CURRENCY_CHOICES,
                         default_currency=('PLN', 'PLN ZŁ'))

    @classmethod
    def get_cash_list(cls, owner):
        return cls.objects.filter(owner=owner)

    def __str__(self):
        return '{} cash {}'.format(self.owner.username, self.my_cash)

# class Land(Resource):
#     LAND_CHOICES = [
#         ('f', 'farmland'),
#         ('b', 'building'),
#     ]
#     AREA_TYPE = [
#         ('h', 'hectare'),
#     ]
#     type = models.CharField(
#         max_length=10,
#         choices=LAND_CHOICES,
#         default='b',
#     )
#     area_unit = models.CharField(max_length=10,
#                                  choices=AREA_TYPE,
#                                  default='h')
