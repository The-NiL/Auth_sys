from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
import views


# making app handler
app = Flask(__name__)
api = Api(app)
jwt = JWTManager(app)

# sercret key for signature
app.config['JWT_SECRET_KEY'] = b"y\xd18S\xae[\x8a\x91J\xbd7\x98Sc%"

# registering api
api.add_resource(views.Index, '/')
api.add_resource(views.UserRegister, '/register')
api.add_resource(views.UserLogin, '/login')
api.add_resource(views.TokenRefresh, '/token/refresh')
api.add_resource(views.UserProfile, '/profile/<string:username>')
api.add_resource(views.EditProfile, '/profile/<string:username>/edit')


