import os

dir = os.listdir('static/images')


for file in dir:
    print(f"'/static/images/{file}',")