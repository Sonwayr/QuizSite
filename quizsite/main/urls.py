from django.urls import path

from .views import *

urlpatterns = [
    path('', MainPage.as_view(), name='main'),
    path('test_info/<int:pk>', ShowTestInfo.as_view(), name='test_info'),
    path('create_test/', CreateTest.as_view(), name='create_test'),
    path('create_questions/<int:test_id>/<int:question_number>', CreateQuestions.as_view(), name='create_questions'),
    path('test/<int:test_id>/question/<int:q_number>', ShowQuestion.as_view(), name='question'),
    path('login/', LoginUser.as_view(), name='login'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('logout/', logout_user, name='logout'),
    path('my_tests/', ShowMyTests.as_view(), name='my_tests'),
    path('my_tests/<int:pk>', RedactOrDeleteTest.as_view(), name='redact_or_delete'),
    path('delete_test/<int:test_id>', delete_test, name='delete_test'),
    path('redact_test/<int:pk>', RedactTest.as_view(), name='redact_test'),
    path('/test/<int:test_id>/question_delete/<int:q_number>', delete_question, name='delete_question'),
    path('redact_test/<int:test_id>/question/<int:q_number>', RedactQuestionForm.as_view(), name='redact_question'),
    path('add_question/<int:test_id>', add_question, name='add_question_from_redact')
]
