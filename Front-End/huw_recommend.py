import sys
from pathlib import Path
from flask import Flask, request, session, render_template, redirect, url_for, g
from flask_restful import Api, Resource, reqparse
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import sql_webshop

app = Flask(__name__)
api = Api(app)

# We define these variables to (optionally) connect to an external MongoDB
# instance.
envvals = ["MONGODBUSER","MONGODBPASSWORD","MONGODBSERVER"]
dbstring = 'mongodb+srv://{0}:{1}@{2}/test?retryWrites=true&w=majority'

# Since we are asked to pass a class rather than an instance of the class to the
# add_resource method, we open the connection to the database outside of the 
# Recom class.
load_dotenv()
if os.getenv(envvals[0]) is not None:
    envvals = list(map(lambda x: str(os.getenv(x)), envvals))
    client = MongoClient(dbstring.format(*envvals))
else:
    client = MongoClient()
database = client.huwebshop 

class Recom(Resource):
    """ This class represents the REST API that provides the recommendations for
    the webshop. At the moment, the API simply returns a random set of products
    to recommend."""

    def get(self, profileid, count):
        """ This function represents the handler for GET requests coming in
        through the API. It currently returns a random sample of products. """
        print(profileid)

        brands = []
        recommendation = sql_webshop.recommendation_collaborative(profileid)

        if recommendation is not None:
            for i in recommendation:
                if i[1] is not None:
                    brands.extend((i[1].keys()))

        if len(brands) > 0:
            # Als er meer dan 0 brands zijn
            collab = sql_webshop.get_collaborative_information(brands)
            collab_brands = set()
            for i in collab:
                [collab_brands.add(j.replace('[', '').replace(']', '').strip()) for j in i[0].split(',')]

            b = sql_webshop.get_brands(tuple(collab_brands))
            b = [i[0] for i in b]
        else:
            # Voor als de hierboven gegeven query geen resultaten oplevert, geef dan gewoon een product om te
            # testen dat deze code operationeel is.
            b = ['8570', '8570', '8570', '8570']

        randcursor = database.products.aggregate([{'$sample': {'size': count}}])
        prodids = list(map(lambda x: x['_id'], list(randcursor)))
        print('B', b)
        print('PROIDS', prodids)
        #return prodids, 200
        return b, 200

# This method binds the Recom class to the REST API, to parse specifically
# requests in the format described below.
api.add_resource(Recom, "/<string:profileid>/<int:count>")