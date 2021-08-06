import pymssql
from flask import jsonify



def dbConnection():

    '''
        Creates a connection to DB, aslo creates
        user table if it doesn't exist
        :returns: connection and cursor
    '''

    try:

        conn = pymssql.connect(
            host = "localhost",
            user = "your_username",
            password = "your_password"
        )


    except:

        return jsonify("connection failed!")


    cur = conn.cursor()
    # calling procedure to create table in case it doesn't exist
    cur.execute("Exec [Information].[dbo].[createTable]")
   
    return conn, cur



def userInfo(username, cur):

        '''
        Selects the user records that matched the username
        :parameters: username as string, connection cursor
        :returns: a list of tuples that each tuple is a record
        '''

        arg = 'Exec [Information].[dbo].[userInfo] @username={}'.format(username)
        # checking if there is a user with the inputed username
        cur.execute(arg)
        user = cur.fetchall()
        
        return user


        
def makeStr(str):

    '''
    Adds quotations to the string for getting them ready to fit
    in SQL query
    :parameters: any string
    :returns: string with double quotations
    '''

    return '"' + str + '"'