from django.contrib import admin
from .models import Poll, Question, Option, Answer


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    readonly_fields = ('number', 'question_type', 'text')

    def has_add_permission(self, request, obj=None):
        return False


class OptionInline(admin.StackedInline):
    model = Option
    extra = 1


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    inlines = (QuestionInline,)
    list_display = ('name', 'start_date', 'end_date', 'is_ready')
    fieldsets = (
        (None, {'fields': ('name', 'is_ready')}),
        ('Dates', {'fields': (('start_date', 'end_date'),)}),
        (None, {'fields': ('description',)})
    )
    search_fields = ('name',)
    save_on_top = True
    list_editable = ('end_date', 'is_ready')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('start_date',)
        return self.readonly_fields


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = (OptionInline,)
    list_display = ('number', 'poll', 'question_type')
    list_filter = ('poll', 'question_type')
    fields = ('poll', 'number', 'question_type', 'text')
    search_fields = ('text',)
    save_on_top = True


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'display_option', 'text')
    list_filter = ('user',)
    search_fields = ('user', 'question')
    readonly_fields = ('user', 'question', 'display_option', 'text')
