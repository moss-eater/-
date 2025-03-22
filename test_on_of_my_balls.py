import random

mylist = ["apple", "banana", "cherry"]

print(random.choices(mylist, weights = [55, 1, 1], k = 1))