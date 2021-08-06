from flask_restful import Resource, reqparse
from passlib.hash import pbkdf2_sha256 as sha256
from datetime import timedelta
from functions import *
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    get_jwt_identity,
    jwt_required
)


conn, cur = dbConnection()


class Index(Resource):

    def get(self):

        return {'message': 'Hello World'}



class UserRegister(Resource):

    def post(self):

        parser = reqparse.RequestParser()

        # required fields
        parser.add_argument('name', help = 'This field cannot be blank', required = True)
        parser.add_argument('username', help = 'This field cannot be blank', required = True)
        parser.add_argument('email', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        
        # getting input data
        data = parser.parse_args()
        
        # hashing password
        password = makeStr(sha256.hash(data['password']))
        email = makeStr(data['email'])
        name, username, password, email = data['name'], data['username'], password, email


        try:

            # calling procedure in order to insert data to DB
            arg = 'Exec [Information].[dbo].[createUser]  @name = {0}, @username = {1},@password = {2}, @email = {3}'.format(name, username, password, email)
            
            cur.execute(arg)
            conn.commit()

            return {
                'message':'Congrats! successfully registered.'
            }
        

        except:

            return {
                'message':'Couldn\'t register, please try again!'
            }



class UserLogin(Resource):

    def post(self):

        parser = reqparse.RequestParser()
        # fields to be required for logging in
        parser.add_argument('username', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        
        # getting input data
        data = parser.parse_args()
        user = userInfo(data['username'], cur)

        # if the username exists we'll check the password
        if (not len(user) == 0):
            
            # verifying inputed pass and user's pass
            # password is user table fourth coloumn
            if ( sha256.verify(data['password'], user[0][3]) ):

                # generating user's access token
                access_token = create_access_token(
                    identity = data['username'],
                    expires_delta = timedelta(minutes = 5)
                )

                # generating user's refresh token
                refresh_token = create_refresh_token(identity = data['username'])
                    
                # giving tokens to the user
                return {
                    'message': 'Logged in as {}'.format(data['username']),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
        

            else:
                return {'message': 'Couldn\'t verify!'}


        else:
            return {'message': 'Wrong credentials!'}



class TokenRefresh(Resource):

    @jwt_required(refresh=True)
    def post(self):

        # extracting identity from refresh token
        current_user = get_jwt_identity()
        # generating new access token for the current user
        access_token = create_access_token(identity = current_user)

        return {'access_token': access_token}
      


class UserProfile(Resource):

    @jwt_required()
    def get(self, username):

        current_user = get_jwt_identity()
        user = userInfo(current_user, cur)

        # if the requested profile is followed by the name of the current user
        # he has access to that page
        if user[0][2].rstrip() == username:

            return {
                'message': 'welcome {}!'.format(user[0][1].rstrip()),
                'name': user[0][1].rstrip(),
                'username': user[0][2].rstrip(),
                'email': user[0][4]
            }


        else:

            return {
                'message': 'Page not found',
            }



class EditProfile(Resource):
     
    @jwt_required()
    def patch(self, username):

        # requesting parser
        parser = reqparse.RequestParser()

        # fields that can be changed
        parser.add_argument('name')
        parser.add_argument('username')
        parser.add_argument('email')
        parser.add_argument('password')
        
        # getting input data
        data = parser.parse_args()

        # current user username
        current_user = get_jwt_identity()
        user = userInfo(current_user, cur)

        username, password, name, email = None, None, None, None


        try:
       
            # checking columns that are requested for updating
            for key, value in data.items():

                    if not value == None:

                        if key == 'username':
                            username = makeStr(value) 
                            
                        elif  key == 'name':
                            name = makeStr(value)  

                        elif key == 'password':
                            password = makeStr(sha256.hash(value))
                            
                        elif key == 'email':
                            email = makeStr(value)
                            

            # updating the columns that user has requested
            arg = 'Exec [Information].[dbo].[userUpdate] @id = {0}, @newUsername = {1}, @newName = {2},@newPassword = {3}, @newEmail = {4}'.format(user[0][0], username, name, password, email)
            new_arg = arg.replace('None', 'NULL')
            
            cur.execute(new_arg)
            conn.commit()
            
            return {'message' : 'Successfully updated!'}
        

        except:
            
            return {'message' : 'Sorry, couldn\'t update!'}
