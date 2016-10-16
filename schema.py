from flask import Flask
from flask_graphql import GraphQLView
import graphene
import requests
from bs4 import BeautifulSoup
from os import environ as env

app = Flask(__name__)

API_KEY = env.get('GOODREADS_API_KEY')

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
    reviews = graphene.List(Review)
    user_reviews = graphene.List(Review, user_id=graphene.ID())
    review = graphene.Field(
        Review,
        id=graphene.ID(),
    )


    def resolve_reviews(self, args, context, info):
        response = requests.get('https://www.goodreads.com/review/recent_reviews.xml?key={}'.format(API_KEY))
        soup = BeautifulSoup(response.text, 'xml')
        reviews = soup.find_all('review')
        return [Review(
            user_id = r.user.id.get_text(),
            id = r.id.get_text(),
            rating = r.rating.get_text(),
            book = Book(
                title = r.book.title.get_text(),
                id = r.book.id.get_text(),
                average_rating = r.book.average_rating.get_text(),
            )
        ) for r in reviews]


    def resolve_user_reviews(self, args, context, info):
        user_id = args.get('user_id')
        request = requests.get('https://www.goodreads.com/review/list/{}.xml?key={}&v=2'.format(user_id, API_KEY))
        soup = BeautifulSoup(request.text, 'xml')
        reviews = soup.find_all('review')
        return [Review(
            id = r.id.get_text(),
            rating = r.rating.get_text(),
            book = Book(
                title = r.book.title.get_text(),
                id = r.book.id.get_text(),
                average_rating = r.book.average_rating.get_text(),
            )
        ) for r in reviews]


    def resolve_review(self, args, context, info):
        id = args.get('id')
        request = requests.get('https://www.goodreads.com/review/show.xml?id={}&key={}'.format(id, API_KEY))
        soup = BeautifulSoup(request.text, 'xml')
        r= soup.review
        return Review(
                id = r.id.get_text(),
                user_id = r.user.id.get_text(),
                rating = r.rating.get_text(),
                book = Book(
                title = r.book.title.get_text(),
                id = r.book.id.get_text(),
                average_rating = r.book.average_rating.get_text(),
            )
        )


schema = graphene.Schema(query=Query)

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))
