from time import sleep

from queries import get_like_items

targets = get_like_items(name="fridge", zip="10020")
for target in targets:
    print(target)
