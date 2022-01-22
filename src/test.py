import itertools
my_dict = {"SHIRT": [0, 1], "HEAD": [0, 1], "HAT": [0, 1], "GLASS": [0, 1]}
keys, values = zip(*my_dict.items())
comb = [dict(zip(keys, v)) for v in itertools.product(*values)]
print(comb)
