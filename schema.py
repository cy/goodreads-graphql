from flask import Flask
from flask_graphql import GraphQLView
import graphene
import requests
from bs4 import BeautifulSoup
from os import environ as env

app = Flask(__name__)

API_KEY = env.get('GOODREADS_API_KEY')

def parse_review_soup(review, args):
    return Review(
        user_id = review.user.id.get_text() if review.user else args.get('user_id'),
        id = review.id.get_text(),
        rating = review.rating.get_text() if review.rating else 0,
        book = Book(
            title = review.book.title.get_text() if review.book.title else '',
            id = review.book.id.get_text(),
            average_rating = review.book.average_rating.get_text() if review.book.average_rating else 0,
        )
    )


def get_latest_reviews(args):
    response = requests.get('https://www.goodreads.com/review/recent_reviews.xml?key={}'.format(API_KEY))
    soup = BeautifulSoup(response.text, 'xml')
    reviews = soup.find_all('review')
    return [parse_review_soup(r, args) for r in reviews]


def get_user_reviews(args):
    user_id = args.get('user_id')
    request = requests.get('https://www.goodreads.com/review/list/{}.xml?key={}&v=2'.format(user_id, API_KEY))
    soup = BeautifulSoup(request.text, 'xml')
    reviews = soup.find_all('review')
    return [parse_review_soup(r, args) for r in reviews]


def get_review(args):
    id = args.get('id')
    request = requests.get('https://www.goodreads.com/review/show.xml?id={}&key={}'.format(id, API_KEY))
    soup = BeautifulSoup(request.text, 'xml')
    r = soup.review
    return parse_review_soup(r, args)


class Book(graphene.ObjectType):
    id = graphene.String()
    title = graphene.String()
    average_rating = graphene.Int()


class Review(graphene.ObjectType):
    user_id = graphene.String(description="Goodreads user id")
    id = graphene.String(description="Id of Goodreads review")
    book = graphene.Field(Book)
    rating = graphene.Int(description="Rate book out of 5, 1 - throw out window 5 - the author is my prophet")


class Query(graphene.ObjectType):
    reviews = graphene.List(
            Review,
            args=dict(
            id=graphene.ID(),
            user_id=graphene.ID(),
        )
    )

    def resolve_reviews(self, args, context, info):
        if len(args.keys()) == 0:
            return get_latest_reviews(args)
        if 'user_id' in args:
            return get_user_reviews(args)
        if 'id' in args:
            return [get_review(args)]


schema = graphene.Schema(query=Query)
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))
