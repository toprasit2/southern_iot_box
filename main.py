from app import app

if __name__ == '__main__':
    # app.run(port=3134, debug=True)  #on local host
    #app.run(host = '0.0.0.0', port = 3134, debug= False)
    app.run(host = '0.0.0.0',  debug=True)