import sys
from pathlib import Path
from flask import Flask, request, session, render_template, redirect, url_for, g
from flask_restful import Api, Resource, reqparse
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import choose_recommendation

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

    def get(self, profileid, count, recom_type):
        """ This function represents the handler for GET requests coming in
        through the API. It currently returns a random sample of products. """

        algo = 0
        p_id = ''
        column = ''
        values = ()

        if ':' in recom_type:
            page, attributes = recom_type.split(':')
            if page == 'shoppingcart':
                algo = -1
                column = 'brand'
                values = attributes.split(';')
            elif page == 'productdetail':
                algo = 3
                p_id = attributes
        #algo = 5

        # choose_recommendation global variables
        choose_recommendation.COUNT = count
        choose_recommendation.PROFILE_ID = profileid
        choose_recommendation.SHUFFLE = True
        recommended = choose_recommendation.choose_algorithm(
            algo,
            p_id=p_id,
            v_id=profileid,
            move_on_if_none=True,
            colomn=column,
            values=values
        )


        randcursor = database.products.aggregate([{'$sample': {'size': count}}])
        prodids = list(map(lambda x: x['_id'], list(randcursor)))
        print('RT:', recom_type)
        #return prodids, 200
        return recommended, 200

# This method binds the Recom class to the REST API, to parse specifically
# requests in the format described below.
api.add_resource(Recom, "/<string:profileid>/<int:count>/<string:recom_type>")
