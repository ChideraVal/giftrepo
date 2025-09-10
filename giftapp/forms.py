from django import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import Gift, User
import random


class CustomAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.fields["username"].widget.attrs['autocomplete'] = 'off'


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.fields["username"].widget.attrs['autocomplete'] = 'off'
        self.fields["email"].widget.attrs['autocomplete'] = 'off'
    
    class Meta:
        model = User
        fields = ['username', 'email', 'gender']


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'gender']
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'off'})
        }


class GiftForm(forms.ModelForm):
    class Meta:
        model = GiftTransaction
        fields = ['quantity', 'is_fastest_finger', 'cost', 'fee', 'is_visible', 'expire_rate', 'drop_rate']

        labels = {
            'is_fastest_finger': 'Fastest Finger (FF)',
            'is_visible': 'Show Gift',
            'cost': 'Early Reveal Cost',
            'fee': 'FF entry fee'
        }

    def clean(self):
        cleaned_data = super().clean()
        quantity = self.cleaned_data.get('quantity')
        expire_rate = cleaned_data.get('expire_rate')
        drop_rate = cleaned_data.get('drop_rate')
        is_fastest_finger = cleaned_data.get('is_fastest_finger')
        early_reveal_cost = cleaned_data.get('cost')
        ff_entry_fee = cleaned_data.get('fee')

        if quantity <= 0:
            raise forms.ValidationError('Quantity must be 1 or more.')
        
        # temporary condition to max expire rate to 24 hrs
        if expire_rate < 1 or expire_rate > 24:
            raise forms.ValidationError('Expire rate must be between 1 and 24.')
        
        # temporary condition to max drop rate to 23 hrs
        if drop_rate > 23:
            raise forms.ValidationError('Drop rate must be between 0 and 23.')
        
        if expire_rate <= drop_rate:
            raise forms.ValidationError('Expire rate must be greater than drop rate.')
        
        if is_fastest_finger and drop_rate == 0:
            raise forms.ValidationError('FF gifts must have drop rates greater than 0.')
        
        # temporary condition to disable wait time for normal gifts
        # if not is_fastest_finger and drop_rate > 0:
        #     raise forms.ValidationError('Drop rates for non FF gifts must be 0.')

        if is_fastest_finger and early_reveal_cost > 0:
            raise forms.ValidationError('FF gifts must not have early reveal cost greater than 0.')

        if not is_fastest_finger and ff_entry_fee:
            raise forms.ValidationError('Only FF gifts can have FF entry fee.')
        
        # FIX ERROR MESSAGE TEXT
        if drop_rate == 0 and early_reveal_cost > 0:
            raise forms.ValidationError('Gifts with drop rate of 0 cannot have early reveal cost greater than 0.')
        
        return cleaned_data
