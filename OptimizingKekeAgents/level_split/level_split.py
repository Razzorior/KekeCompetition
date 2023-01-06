import random

random.seed(1)

with open("levels.json", "r") as levelfile:
    lines = levelfile.readlines()

levels = lines[1:-1]

train_idx = set(random.sample(range(len(levels)), 50))
train_levels = [line for i, line in enumerate(levels) if i in train_idx]
test_levels = [line for i, line in enumerate(levels) if i not in train_idx]
print("number of train levels: ", len(train_levels))
print("number of test levels: ", len(test_levels))

with open("train_LEVELS.json", "w") as train_file:
    train_file.write(lines[0])
    for train_lvl in train_levels[:-1]:
        train_file.write(train_lvl)
    if train_levels[-1].endswith(",\n"):
        train_file.write(train_levels[-1][:-2] + "\n")
    else:
        train_file.write(train_levels[-1])
    train_file.write(lines[-1])

with open("test_LEVELS.json", "w") as test_file:
    test_file.write(lines[0])
    for test_lvl in test_levels[:-1]:
        test_file.write(test_lvl)
    if test_levels[-1].endswith(",\n"):
        test_file.write(test_levels[-1][:-2]+"\n")
    else:
        test_file.write(test_levels[-1])

    test_file.write(lines[-1])