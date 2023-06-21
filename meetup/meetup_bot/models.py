from django.db import models

ROLE = [
    ('guest', 'Гость'),
    ('speaker', 'Спикер'),
    ('organizer', 'Организатор')
]


class Member(models.Model):
    name = models.CharField('ФИО участника', max_length=200, null=True, blank=True)
    telegram = models.CharField('Телеграм', max_length=200, unique=True)
    role = models.CharField('Участник или Гость?', max_length=10, choices=ROLE),
    company = models.CharField('Компания', max_length=200, null=True, blank=True),
    job = models.CharField('Компания', max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class Presentation(models.Model):
    number = models.IntegerField(verbose_name='Порядковый номер доклада')
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='presentations',
        verbose_name='Спикер'
    )
    name = models.CharField('Тема выступления', max_length=200)
    duration = models.DurationField(verbose_name='Продолжительность доклада')


class Question(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Спрашивающий'
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='speaker_questions',
        verbose_name='Спикер'
    )
    question = models.CharField('Текст вопроса', max_length=200)
