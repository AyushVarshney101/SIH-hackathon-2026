from django import forms

from .models import Profile, Project, Rating


class RegistrationForm(forms.Form):
    name = forms.CharField(max_length=150)
    username = forms.CharField(max_length=150)
    registering_as = forms.ChoiceField(choices=Profile.RegisteringAs.choices)
    address = forms.CharField(max_length=255)
    machines_available = forms.IntegerField(required=False, min_value=0)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        from django.contrib.auth.models import User

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('That username is already in use.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            self.add_error('confirm_password', 'Passwords do not match.')

        registering_as = cleaned_data.get('registering_as')
        if registering_as == Profile.RegisteringAs.MACHINERY and cleaned_data.get('machines_available') is None:
            self.add_error('machines_available', 'Enter the number of available machines.')
        return cleaned_data


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['land_owner'].queryset = Profile.objects.filter(
            registering_as=Profile.RegisteringAs.LAND_OWNER,
        )
        self.fields['land_owner'].empty_label = 'Looking for Land'
        self.fields['labour'].queryset = Profile.objects.filter(
            registering_as=Profile.RegisteringAs.LABOUR,
        )
        self.fields['labour'].empty_label = 'Looking for Labour'
        self.fields['machinery_contributor'].queryset = Profile.objects.filter(
            registering_as=Profile.RegisteringAs.MACHINERY,
        )
        self.fields['machinery_contributor'].empty_label = 'Looking for Machinery'

    class Meta:
        model = Project
        fields = [
            'project_name',
            'address',
            'land_owner',
            'labour',
            'machinery_contributor',
            'expected_timeline',
            'invested_money',
            'expected_revenue',
            'description',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'project_name': 'Project name',
            'land_owner': 'Land owner',
            'labour': 'Manual labour',
            'machinery_contributor': 'Farming machinery contributor',
            'expected_timeline': 'Expected timeline',
            'invested_money': 'Invested money',
            'expected_revenue': 'Expected revenue',
        }


class RatingForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=[(value, '★' * value + '☆' * (5 - value)) for value in range(1, 6)],
        coerce=int,
        label='Rating',
    )

    class Meta:
        model = Rating
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.TextInput(attrs={'placeholder': 'Optional comment'}),
        }