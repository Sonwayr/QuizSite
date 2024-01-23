from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse_lazy


class Test(models.Model):
    owner = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Владелец')
    name = models.CharField(max_length=255, blank=False, verbose_name='Название теста', unique=True)
    description = models.TextField(blank=False, verbose_name='Описание теста')
    question_quantity = models.IntegerField(blank=False, verbose_name='Кол-во вопросов',
                                            validators=[MinValueValidator(1), MaxValueValidator(24)])

    def get_absolute_url_info(self):
        return reverse_lazy('test_info', kwargs={'pk': self.pk})

    def get_absolute_url_redact(self):
        return reverse_lazy('redact_or_delete', kwargs={'pk': self.pk})


class Question(models.Model):
    question = models.TextField(blank=False, verbose_name='Вопрос')
    correct_answer = models.CharField(max_length=255, verbose_name='Правильный ответ')
    incorrect_answer_1 = models.CharField(max_length=255, verbose_name='Неправильный ответ')
    incorrect_answer_2 = models.CharField(max_length=255, verbose_name='Неправильный ответ')
    incorrect_answer_3 = models.CharField(max_length=255, verbose_name='Неправильный ответ')
    test = models.ForeignKey('Test', on_delete=models.CASCADE, verbose_name='Тест', related_name='questions')
    number = models.IntegerField(verbose_name='Номер вопроса')

    def __str__(self):
        return self.question
