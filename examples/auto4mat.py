import os

path = os.getcwd()
dir_list = os.listdir(path)

for file in dir_list:
    if file.endswith(".py"):
        res = os.system("pyupgrade " + file)
        print(res)
        res = os.system("isort " + file)
        print(res)
        res = os.system("black " + file)
        print(res)

res = os.system("pipreqs --force " + path)
print(res)
