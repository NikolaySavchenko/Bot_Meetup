from django.db import models

ROLE = [
    ('guest', 'Гость'),
    ('speaker', 'Спикер'),
    ('organizer', 'Организатор')
]


class Member(models.Model):
    telegram = models.CharField('Телеграм', max_length=200, unique=True)
    role = models.CharField(
        'Спикер или Гость?',
        max_length=10,
        choices=ROLE,
        default='guest'
    )
    donation = models.FloatField('Сумма доната', null=True, default=0)


    def __str__(self):
        return self.name


class Presentation(models.Model):
    start_time = models.DateTimeField(verbose_name='Время начала доклада')
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='presentations',
        verbose_name='Спикер'
    )
    topic = models.CharField('Тема выступления', max_length=200)
    duration = models.DurationField(verbose_name='Продолжительность доклада')
    is_active_now = models.BooleanField(default=False)


    def __str__(self):
        return self.member


class Form(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Спрашивающий'
    )
    name = models.CharField('Ваше имя', max_length=200, blank=True)
    age = models.IntegerField('Сколько вам лет?')
    company = models.CharField('Компания', max_length=100, blank=True)
    job = models.CharField('Ваша должность', max_length=100, blank=True)
    stack = models.CharField('С какими технологиями работаете?', max_length=200, blank=True)
    hobby = models.CharField('Ваше хобби?', max_length=100, blank=True)
    goal = models.CharField('Цель знакомства?', max_length=100, blank=True)
    region = models.CharField('Регион', max_length=100, blank=True)


