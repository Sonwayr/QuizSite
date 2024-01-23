from django.shortcuts import render, redirect, get_object_or_404

from main.models import *


class QuestionMixin:
    def process_question(self, test_id, question_number, question, form):
        session = self.request.session
        session_key = session.session_key
        question_quantity = question.test.question_quantity
        if form.is_valid():
            if session_key:
                tests_in_progress = session.get('tests_in_progress', [])
                if test_id not in tests_in_progress:
                    tests_in_progress.append(test_id)
                    session['tests_in_progress'] = tests_in_progress
                answered_questions = session.get(f'answered_questions_{test_id}', [])
                answered_questions.append(question_number)
                self.request.session[f'answered_questions_{test_id}'] = answered_questions

                answer = form.cleaned_data['answer']
                if answer == question.correct_answer:
                    correct_answers = session.get(f'correct_answers_{test_id}', 0)
                    correct_answers += 1
                    session[f'correct_answers_{test_id}'] = correct_answers
                else:
                    incorrect_answers = session.get(f'incorrect_answers_{test_id}', 0)
                    incorrect_answers += 1
                    session[f'incorrect_answers_{test_id}'] = incorrect_answers

        next_q_number = question_number + 1
        if next_q_number > question_quantity:
            correct_answered = session.get(f'correct_answers_{test_id}', 0)
            incorrect_answered = session.get(f'incorrect_answers_{test_id}', 0)
            result = correct_answered * 100 // question_quantity

            session['tests_in_progress'].remove(test_id)
            session[f'correct_answers_{test_id}'] = 0
            session[f'incorrect_answers_{test_id}'] = 0
            session[f'answered_questions_{test_id}'] = []
            context = {'correct_answers': correct_answered, 'incorrect_answers': incorrect_answered,
                       'result': result, 'test_id': test_id, 'question_quantity': question_quantity}
            return render(self.request, 'main/result.html', context=context)

        return redirect('question', test_id=test_id, q_number=next_q_number)

    @staticmethod
    def get_redirect(test_id, question_number, session):
        session_key = session.session_key
        if session_key:
            answered_questions = session.get(f'answered_questions_{test_id}', [])
            tests_in_progress = session.get('tests_in_progress', [])
            if test_id in tests_in_progress:
                if question_number in answered_questions:
                    next_q_number = question_number + 1
                    return redirect('question', test_id=test_id, q_number=next_q_number)
        return None

    def get_data(self, need_test_id=True):
        test_id = self.kwargs.get('test_id')
        question_number = self.kwargs.get('q_number')
        test = get_object_or_404(Test, pk=test_id)
        if need_test_id:
            return test_id, question_number, test
        else:

            return question_number, test
