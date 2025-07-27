from django.core.management.base import BaseCommand
from core.models import Category

class Command(BaseCommand):
    help = 'Creates default system categories'

    def handle(self, *args, **kwargs):
        default_categories = [
            {
                'name': 'Food & Dining',
                'description': 'Restaurants, cafes, groceries, and food delivery',
                'keywords': 'restaurant,cafe,food,grocery,supermarket,burger,pizza,chicken,market,eatery,diner,bakery',
            },
            {
                'name': 'Transportation',
                'description': 'Public transport, ride-sharing, fuel, and vehicle maintenance',
                'keywords': 'uber,bolt,taxi,transport,fuel,petrol,bus,train,flight,airline,car,auto,garage',
            },
            {
                'name': 'Utilities',
                'description': 'Electricity, water, gas, internet, and phone bills',
                'keywords': 'electricity,water,gas,dstv,gotv,internet,wifi,phone,mobile,utility,bill,power,telecom',
            },
            {
                'name': 'Entertainment',
                'description': 'Movies, streaming services, events, and recreation',
                'keywords': 'cinema,movie,theatre,netflix,spotify,game,betting,entertainment,concert,show,ticket',
            },
            {
                'name': 'Shopping',
                'description': 'Retail purchases, clothing, and electronics',
                'keywords': 'mall,store,shop,retail,clothing,fashion,electronics,gadget,amazon,jumia,konga',
            },
            {
                'name': 'Healthcare',
                'description': 'Medical expenses, pharmacy, and health insurance',
                'keywords': 'hospital,clinic,pharmacy,medical,doctor,dental,health,drug,medicine,insurance',
            },
            {
                'name': 'Education',
                'description': 'School fees, courses, books, and training',
                'keywords': 'school,college,university,tuition,course,training,education,book,class,seminar',
            },
            {
                'name': 'Housing',
                'description': 'Rent, mortgage, and home maintenance',
                'keywords': 'rent,house,apartment,mortgage,maintenance,repair,property,estate,accommodation',
            },
            {
                'name': 'Income',
                'description': 'Salary, investments, and other income',
                'keywords': 'salary,wage,payment,credit,income,interest,dividend,investment,return',
            },
            {
                'name': 'Other',
                'description': 'Uncategorized transactions',
                'keywords': '',
            },
        ]

        for cat_data in default_categories:
            Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'keywords': cat_data['keywords'],
                    'is_system': True,
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully created default categories'))