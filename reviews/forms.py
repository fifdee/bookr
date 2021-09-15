from django import forms
from .models import Publisher, Review


class SearchForm(forms.Form):
    CHOICES = (('title', 'Title'), ('contributor', 'Contributor'))

    search = forms.CharField(required=False, min_length=3)
    search_in = forms.ChoiceField(required=False, choices=CHOICES)


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = "__all__"


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        exclude = ["date_edited", "book"]

    rating = forms.IntegerField(min_value=0, max_value=5)