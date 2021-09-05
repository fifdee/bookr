from django.shortcuts import render, get_object_or_404
from .models import Book, Review
from .utils import average_rating
from .forms import SearchForm


def book_list(request):
    books = Book.objects.all()
    book_list = []
    for book in books:
        reviews = book.review_set.all()
        if reviews:
            book_rating = average_rating([review.rating for review in reviews])
            number_of_reviews = len(reviews)
        else:
            book_rating = None
            number_of_reviews = 0
        book_list.append({'book': book, 'book_rating': book_rating, 'number_of_reviews': number_of_reviews})

    context = {'book_list': book_list}

    return render(request, 'reviews/books_list.html', context)


def book_details(request, id):
    book = get_object_or_404(Book, pk=id)
    reviews = book.review_set.all()
    if reviews:
        book_rating = average_rating([review.rating for review in reviews])
    else:
        book_rating = None
    item = {'book': book, 'book_rating': book_rating, 'reviews': reviews}
    context = {'item': item}

    return render(request, 'reviews/book_details.html', context)


def book_search(request):
    form = SearchForm(request.GET)
    books = set()
    context = {}
    contributors = []
    if form.is_valid():
        search = form.cleaned_data['search']
        search_in = form.cleaned_data['search_in']

        if search and search_in != 'contributor':
            books.update(Book.objects.filter(title__icontains=search))

        if search and search_in == 'contributor':
            books.update(Book.objects.filter(contributors__last_names__icontains=search))
            books.update(Book.objects.filter(contributors__first_names__icontains=search))

        for book in books:
            for contributor in book.bookcontributor_set.all():
                contributors.append(contributor.contributor.first_names + ' ' + contributor.contributor.last_names)

        context = {'form': form, 'search': search, 'books': books, 'contributors': ', '.join(contributors)}

    return render(request, 'reviews/book_search.html', context)