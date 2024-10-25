from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField
from .models import Lead, Agent, Category

User = get_user_model()

class LeadModelForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = (
            'first_name',
            'last_name',
            'age',
            'agent',
            "description",
            "phone_number",
            "email"
        )

class LeadForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    age = forms.IntegerField(min_value=0)

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}

class AssignAgentForm(forms.Form):
    # agent = forms.ChoiceField(choices=(
    #     ('Agent 1', "Agent 1 Full Name"),
    #     ('Agent 2', "Agent 2 Full Name")
    # ))
    agent = forms.ModelChoiceField(queryset=Agent.objects.none())

    def __init__(self, *args, **kwargs):
        # print(kwargs)
        request = kwargs.pop("request")
        print(request.user)
        agents = Agent.objects.filter(organization=request.user.userprofile)
        # after made filter to apply on "agent" field( agent = forms.ModelChoiceField(queryset=Agent.objects.none()) )...we can do this way...
        # it is dictionary w/c the way we can access each field
        # it is passing the "__init__" function with original(not modified) arguments...after pop-out needed element "request"...unless it print error...
        # cuz we override the built-in function
        super(AssignAgentForm, self).__init__(*args, **kwargs)
        self.fields["agent"].queryset = agents

class LeadCategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = (
            'category',
        )

class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = (
            'name',
        )