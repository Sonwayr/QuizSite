from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from .forms import *
from .utils import *


class MainPage(ListView):
    model = Test
    template_name = 'main/main_page.html'
    extra_context = {'title': "Главная страница"}
    context_object_name = 'tests'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get('search')
        if search:
            context['search'] = search
        return context

    def get_queryset(self):
        search = self.request.GET.get('search')
        tests = Test.objects.all()

        if search:
            tests = tests.filter(name__contains=search)

        return tests


class ShowMyTests(ListView, UserPassesTestMixin):
    login_url = '/login/'
    model = Test
    template_name = 'main/show_my_tests.html'
    extra_context = {'title': 'Мои тесты'}
    context_object_name = 'tests'
    paginate_by = 10

    def get_queryset(self):
        user_id = self.request.user.pk
        tests = Test.objects.filter(owner_id=user_id)
        return tests


class CreateTest(UserPassesTestMixin, CreateView):
    login_url = '/login/'
    template_name = 'main/create_test.html'
    form_class = CreateTestForm
    extra_context = {'title': 'Создание теста'}

    def test_func(self):
        return self.request.user.is_superuser  # Проверяем, является ли пользователь суперпользователем

    def handle_no_permission(self):
        # Обработка случая, когда пользователь не имеет прав доступа
        return HttpResponse("Доступ запрещен")

    def form_valid(self, form):
        test = form.instance
        test.owner = self.request.user
        test.save()
        return redirect('create_questions', test_id=test.pk, question_number=1)


class CreateQuestions(UserPassesTestMixin, CreateView, QuestionMixin):
    login_url = '/login/'
    template_name = 'main/create_questions.html'
    form_class = CreateQuestionsForm

    def test_func(self):
        return self.request.user.is_superuser  # Проверяем, является ли пользователь суперпользователем

    def handle_no_permission(self):
        # Обработка случая, когда пользователь не имеет прав доступа
        return HttpResponse("Доступ запрещен")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        test_id = self.kwargs.get('test_id')
        question_number = self.kwargs.get('question_number')
        test = get_object_or_404(Test, id=test_id)
        question_quantity = test.question_quantity
        allowed = self.is_question_creation_allowed(question_number, question_quantity)
        context['test_id'] = test_id
        context['allowed'] = allowed
        context['question_number'] = question_number
        context['question_quantity'] = question_quantity
        return context

    def form_valid(self, form):
        question = form.instance
        test_id = self.kwargs.get('test_id')
        test = get_object_or_404(Test, pk=test_id)
        question.test_id = test_id
        test_questions_quantity = test.question_quantity
        question_number = self.kwargs.get('question_number')
        question.number = question_number
        question.save()

        if test_questions_quantity == test.questions.count():
            return redirect('main')

        return redirect('create_questions', test_id=test_id, question_number=question_number + 1)

    def is_question_creation_allowed(self, question_number, question_quantity):
        if 0 < question_number <= question_quantity:
            question = self.get_question_by_number(question_number)
            return question is None
        return False

    def get_question_by_number(self, question_number):
        test_id = self.kwargs.get('test_id')
        try:
            return Question.objects.get(test_id=test_id, number=question_number)
        except Question.DoesNotExist:
            return None


class ShowTestInfo(DetailView):
    template_name = 'main/show_test_info.html'
    model = Test
    extra_context = {'title': 'О тесте'}
    context_object_name = 'test'

    def get_object(self, queryset=None):
        test_id = self.kwargs.get('pk')  # Получение идентификатора теста из URL-параметра
        obj = get_object_or_404(Test, id=test_id)
        return obj


class ShowQuestion(LoginRequiredMixin, DetailView, QuestionMixin):
    template_name = 'main/question.html'
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        import random
        test_id, question_number, test = self.get_data()
        question_quantity = test.question_quantity
        if question_number > test.question_quantity:
            return redirect('test_info', pk=test_id)
        session = self.request.session
        do_redirect = self.get_redirect(test_id=test_id, question_number=question_number, session=session)
        if do_redirect:
            return do_redirect
        question = get_object_or_404(Question, number=question_number, test=test)

        choices = [
                      (getattr(question, f'incorrect_answer_{i}'), getattr(question, f'incorrect_answer_{i}'))
                      for i in range(1, 4)
                  ] + [(question.correct_answer, question.correct_answer)]

        question_name = question.question
        random.shuffle(choices)
        form = QuestionForm(choices=choices, question_name=question_name, question_number=question_number,
                            question_quantity=question_quantity)
        return render(request, self.template_name, {'title': 'Вопрос', 'form': form})

    def post(self, request, *args, **kwargs):
        test_id, question_number, test = self.get_data()
        question_quantity = test.question_quantity
        question = get_object_or_404(Question, number=question_number, test=test)

        choices = [
                      (getattr(question, f'incorrect_answer_{i}'), getattr(question, f'incorrect_answer_{i}'))
                      for i in range(1, 4)
                  ] + [(question.correct_answer, question.correct_answer)]

        question_name = question.question
        form = QuestionForm(request.POST, choices=choices, question_name=question_name, question_number=question_number,
                            question_quantity=question_quantity)

        return self.process_question(test_id, question_number, question, form)


class RegisterUser(CreateView):
    template_name = 'main/register.html'  # Шаблон для отображения формы регистрации
    form_class = RegisterUserForm  # Форма для регистрации пользователя
    success_url = reverse_lazy('login')  # URL для перенаправления после успешной регистрации
    extra_context = {'title': 'Регистрация'}

    def form_valid(self, form):
        # При сохранении формы, создаем пользователя и автоматически выполняем вход
        user = form.save()
        login(self.request, user)
        return redirect('main')


class LoginUser(LoginView):
    template_name = 'main/login.html'
    form_class = LoginUserForm
    extra_context = {'title': 'Авторизация'}

    def get_success_url(self):
        return reverse_lazy('main')


def logout_user(request):
    logout(request)
    return redirect('login')


class RedactOrDeleteTest(UserPassesTestMixin, DetailView):
    login_url = '/login/'
    model = Test
    template_name = 'main/show_info_for_redact.html'
    extra_context = {'title': 'Редактирование теста'}
    context_object_name = 'test'

    def test_func(self):
        return self.request.user.is_superuser  # Проверяем, является ли пользователь суперпользователем


@user_passes_test(lambda u: u.is_superuser)
def delete_test(request, test_id):
    test = Test.objects.get(pk=test_id)
    questions = test.questions.all()
    questions.delete()
    test.delete()
    return redirect('my_tests')


class RedactTest(DetailView, UserPassesTestMixin):
    login_url = '/login/'
    template_name = 'main/questions_for_redact.html'
    extra_context = {'title': 'Редактирование вопросов'}
    context_object_name = 'questions'
    model = Test

    def get_object(self, queryset=None):
        test_id = self.kwargs.get('pk')
        test = get_object_or_404(Test, pk=test_id)
        obj = test.questions.all()
        return obj

    def test_func(self):
        return self.request.user.is_superuser  # Проверяем, является ли пользователь суперпользователем


class RedactQuestionForm(UserPassesTestMixin, QuestionMixin, UpdateView):
    login_url = '/login/'
    model = Question
    template_name = 'main/question_redact.html'
    extra_context = {'title': 'Редактирование вопроса'}
    context_object_name = 'question'
    form_class = CreateQuestionsForm

    def test_func(self):
        return self.request.user.is_superuser

    def get_object(self, queryset=None):
        q_number, test = self.get_data(need_test_id=False)
        obj = test.questions.get(number=q_number)
        return obj

    def form_valid(self, form):
        question = form.instance  # Получаем объект теста из формы
        question.save()
        test_id = question.test_id  # Получаем test_id
        return redirect('redact_test', pk=test_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        test_id = self.kwargs.get('test_id')
        context['test_id'] = test_id
        return context


@user_passes_test(lambda u: u.is_superuser)
def delete_question(request, test_id, q_number):
    test = get_object_or_404(Test, pk=test_id)
    questions = test.questions.all()
    questions[q_number - 1].delete()
    test.question_quantity -= 1
    test.save()
    for q in questions[q_number:]:
        q.number -= 1
        q.save()
    return redirect('redact_test', pk=test_id)


@user_passes_test(lambda u: u.is_superuser)
def add_question(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    test.question_quantity += 1
    test.save()
    q_number = test.question_quantity
    return redirect('create_questions', test_id=test_id, question_number=q_number)
