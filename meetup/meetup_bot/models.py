import datetime

from django.db import models

ROLE = [
    ('guest', 'Гость'),
    ('speaker', 'Спикер'),
    ('organizer', 'Организатор')
]


class Member(models.Model):
    telegram_id = models.IntegerField('telegram_id')
    telegram_name = models.CharField(verbose_name='Телеграм', max_length=200, unique=True)
    role = models.CharField(
        verbose_name='Спикер или Гость?',
        max_length=10,
        choices=ROLE,
        default='guest'
    )

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'

    def __str__(self):
        return self.telegram_name


class Donation(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='donation',
        verbose_name='Участник'
    )
    donation = models.FloatField(verbose_name='Сумма доната', null=True, default=0)

    class Meta:
        verbose_name = 'Донаты'
        verbose_name_plural = 'Донаты'

    def __str__(self):
        return self.member


class Presentation(models.Model):
    start_time = models.DateTimeField(verbose_name='Время начала доклада')
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='presentations',
        verbose_name='Спикер'
    )
    topic = models.CharField(verbose_name='Тема выступления', max_length=200)
    duration = models.DurationField(
        verbose_name='Продолжительность доклада',
        default=datetime.timedelta(days=0, seconds=2400)
    )
    is_active_now = models.BooleanField(verbose_name='Проходит прямо сейчас', default=False)

    class Meta:
        verbose_name = 'Презентация'
        verbose_name_plural = 'Презентации'


class Form(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='forms',
        verbose_name='Участник'
    )
    name = models.CharField(verbose_name='Ваше имя', max_length=200, blank=True)
    age = models.IntegerField(verbose_name='Сколько вам лет?', null=True, blank=True)
    company = models.CharField(verbose_name='Компания', max_length=100, blank=True)
    job = models.CharField(verbose_name='Ваша должность', max_length=100, blank=True)
    stack = models.CharField(
        verbose_name='С какими технологиями работаете?',
        max_length=200,
        blank=True
    )
    hobby = models.CharField(verbose_name='Ваше хобби?', max_length=100, blank=True)
    goal = models.CharField(verbose_name='Цель знакомства?', max_length=100, blank=True)
    region = models.CharField(verbose_name='Регион', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Анкета'
        verbose_name_plural = 'Анкеты'

    def __str__(self):
        return self.name, self.job, self.region
