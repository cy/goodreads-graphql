# 📗 goodreads-graphql

Python Graphql wrapper over the [Goodreads API](https://www.goodreads.com/api), which likes to return xml :/

Limited to reviews... and fields I cherry-picked.

# 🌳 key dependencies
- [Graphene](https://github.com/graphql-python/graphene/)
- [flask-graphql](https://github.com/graphql-python/flask-graphql)

# 🏃 run it
```
$ GOODREADS_API_KEY={key} FLASK_APP=schema.py flask run
```
