from firebase import firebase
firebase = firebase.FirebaseApplication('https://southern-iot-box.firebaseio.com', None)
result = firebase.get('/Users', None)
# firebase.put('/app/data', '-LHN_VMoZ4nnjPfuIPYT23',
#             {   'title':'helloworld34',
#                 'day' : v['day'],
#                 'link' : v['link'],
#                 'month' : v['month'],
#                 'thumbnail' : v['thumbnail'],
#                 'year' : v['year']
#             })
for key,value in result.items():
    if 'admin@gmail.com' == value['email']:
        print("Noob")