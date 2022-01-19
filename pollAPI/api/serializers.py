from rest_framework import serializers
from rest_framework.serializers import ValidationError
import re

from .models import Poll, Question, Option, Answer


class OptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = ('id', 'number', 'text')


class QuestionSerializer(serializers.ModelSerializer):

    options = OptionSerializer(source='option_set', many=True)
    question_type = serializers.CharField(source='get_question_type_display')

    class Meta:
        model = Question
        fields = ('id', 'number', 'question_type', 'text', 'options')


class PollListSerializer(serializers.ModelSerializer):

    start_date = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S')
    end_date = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S')

    class Meta:
        model = Poll
        fields = ('id', 'name', 'start_date', 'end_date', 'description')


class PollDetailSerializer(serializers.ModelSerializer):

    start_date = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S')
    end_date = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S')
    questions = QuestionSerializer(source='question_set', many=True)

    class Meta:
        model = Poll
        fields = ('id', 'name', 'start_date', 'end_date', 'description', 'questions')


class AnswerCreateSerializer(serializers.ModelSerializer):

    option = serializers.CharField(required=False)

    class Meta:
        model = Answer
        fields = ('question', 'option', 'text')

    def validate(self, data):

        if data['question'].poll not in Poll.objects.active():
            raise ValidationError('The poll is unavailable')

        question_type = data['question'].question_type
        text = data.get('text')
        options = data.get('option')

        if not any([text, options]):
            raise ValidationError('No answer was given')

        # Validate text answers
        if question_type == 'T' and not data.get('text'):
            raise ValidationError('The answer to this type of question must contain "text"')

        # Validate answers to questions with choices
        if question_type != 'T':
            if not data.get('option'):
                raise ValidationError('The answer to this type of question must contain "options"')
            if not re.match(r'^\d+(,\d+)*$', options):
                raise ValidationError('Options must be a comma-separated string with option id')
            if question_type == 'OC' and not re.match(r'^\d+$', options):
                raise ValidationError('The answer to this type of question must be a number (option id)')

            # Make sure that the answer provided options from this question
            option_ids = list(map(int, data['option'].split(',')))
            option_objects = Option.objects.filter(pk__in=option_ids)
            if any(opt.question != data['question'] for opt in option_objects):
                raise ValidationError('Incorrect answer IDs. Check if they are all related to the target question')

        return data

    def create(self, validated_data):
        if validated_data.get('option'):
            # parse comma-separated IDs
            option_ids = list(map(int, validated_data['option'].split(',')))
            answer_data = {key: value for key, value in validated_data.items() if key not in ['option', 'text']}
            option_objects = Option.objects.filter(pk__in=option_ids)
            answer, _ = Answer.objects.get_or_create(**answer_data)

            for opt in option_objects:
                answer.option.add(opt)
        else:
            answer, _ = Answer.objects.get_or_create(**validated_data)
        return answer


class QuestionReportSerializer(QuestionSerializer):
    """ Serializer of the question displayed in the /my_polls/ report """

    answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'number', 'question_type', 'text', 'options', 'answer')

    def get_answer(self, obj):
        ans = Answer.objects.get(user=self.context['request'].user, question=obj)
        if obj.question_type == 'T':
            return ans.text
        else:
            return ' | '.join([f'({opt.number}) {opt.text}' for opt in ans.option.all()])


class MyPollsListSerializer(PollListSerializer):

    questions = QuestionReportSerializer(source='question_set', many=True)

    class Meta:
        model = Poll
        fields = ('id', 'name', 'start_date', 'end_date', 'description', 'questions')
