import random

random.seed(1)

with open("levels.json", "r") as levelfile:
    lines = levelfile.readlines()

levels = lines[1:-1]

train_idx = set(random.sample(range(len(levels)), int(0.6*len(levels))))
train_levels = [line for i, line in enumerate(levels) if i in train_idx]
test_levels = [line for i, line in enumerate(levels) if i not in train_idx]
print(len(test_levels))
print(len(train_levels))

with open("train_LEVELS.json", "w") as train_file:
    train_file.write(lines[0])
    for train_lvl in train_levels:
        train_file.write(train_lvl)
    train_file.write(lines[-1])

with open("test_LEVELS.json", "w") as test_file:
    test_file.write(lines[0])
    for test_lvl in test_levels:
        test_file.write(test_lvl)
    test_file.write(lines[-1])