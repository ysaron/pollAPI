from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.timezone import now


class PollManager(models.Manager):

    def active(self):
        return super().get_queryset().filter(start_date__lt=now(), end_date__gt=now(), is_ready=True)


class Poll(models.Model):

    name = models.CharField(max_length=255, verbose_name='Name')
    start_date = models.DateTimeField(verbose_name='Beginning date')
    end_date = models.DateTimeField(verbose_name='Expiration date')
    description = models.TextField(verbose_name='Description')
    is_ready = models.BooleanField(default=False, verbose_name='Ready')

    objects = PollManager()

    class Meta:
        verbose_name = 'Poll'
        verbose_name_plural = 'Polls'
        ordering = ['start_date']

    def __str__(self):
        return self.name

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError('Everything that has a beginning has an end... AFTER the beginning. '
                                  'Please check that the dates provided are correct.')


class Question(models.Model):

    TYPES = [
        ('T', 'Text'),
        ('OC', 'One choice'),
        ('MC', 'Multiple choices'),
    ]

    text = models.TextField(verbose_name='Text')
    question_type = models.CharField(max_length=2, choices=TYPES, verbose_name='Type')
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, verbose_name='Poll')
    number = models.PositiveSmallIntegerField(verbose_name='Index number')

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        unique_together = ['number', 'poll']

    def __str__(self):
        return f'({self.poll.name}; question №{self.number}): {self.text}'


class Option(models.Model):

    question: Question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Question')
    number = models.PositiveSmallIntegerField(verbose_name='Index number')
    text = models.TextField(verbose_name='Text')

    class Meta:
        verbose_name = 'Option'
        verbose_name_plural = 'Options'
        ordering = ['number']
        unique_together = ['number', 'question']

    def __str__(self):
        return f'Option №{self.number}: {self.text}'


class Answer(models.Model):

    user: User = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Participant', null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Question')
    option: Option = models.ManyToManyField(Option, verbose_name='Selected option(s)', null=True)
    text = models.TextField(verbose_name='Text answer', default='')

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        ordering = ['question']

    def __str__(self):
        return f'{self.user} | {self.question.text} | {self.option}'

    def display_option(self):
        return ' | '.join([f'Option №{opt.number}: {opt.text}' for opt in self.option.all()])

    display_option.short_description = 'Answers'
