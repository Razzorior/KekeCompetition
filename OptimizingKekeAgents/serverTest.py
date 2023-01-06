import socketio

# standard Python
sio = socketio.Client()
sio.connect('http://localhost:8080', namespaces=['/'])


LEVEL_SETS = ["demo_LEVELS",
              "empty_LEVELS",
              "full_biy_LEVELS",
              "search_biy_LEVELS",
              "test_LEVELS",
              "user_milk_biy_LEVELS"]

level_set = LEVEL_SETS[2]
agent = "weird_parameterized"

available_levels = []
unsolved_levels = []
stats = []


@sio.on('level-set-list')
def on_level_set_list(levelsetlist):
    print('Level Sets:')
    # add list of level sets to the dropdown
    for lvl in levelsetlist:
        print(lvl)
    print()


@sio.on('agent-list')
def on_agent_list(agentlist):
    print("Agent Sets:")
    # add list of agents sets to the other dropdown
    for ag in agentlist:
        print(ag)
    print()


def load_level_set(level_set):
    sio.emit('get-level-set', {"levelSet": (level_set)})


@sio.on('return-level-json')
def process_level_set_json(level_set_json):
    global unsolved_levels, available_levels
    available_levels = [lvl["id"] for lvl in level_set_json]
    unsolved_levels = available_levels.copy()
    print("levels in level_set", unsolved_levels)
    solve_level_set()


def solve_next_level():
    # all levels solved
    if len(unsolved_levels) == 0:
        print("SOLVED ALL LEVELS!")
        print("performance:", sum(stats)/len(stats))
        return

    # pass the next unsolved level data to the server to solve it
    sio.emit('solve-level', {"agent": agent,
                             "levelSet": level_set,
                             "levelID": unsolved_levels[0],
                             "params": [1, 1, 1, 1, 1, 0, 0, 1]})


@sio.on('finish-level')
def on_finish_level(lvl):
    print("GOT LEVEL DATA: ", lvl['id'])

    # update the level row with the new info
    ss = lvl['won_level']
    stats.append(ss)

    unsolved_levels.pop(0)

    # solve the next level if possible
    solve_next_level()


def solve_level_set():
    # solves an entire level_set
    sio.emit('solve-level-set', {"agent": agent, "levelSet": level_set, "params": [1, 1, 1, 1, 1, 0, 0, 1]})


@sio.on('finish-level-set')
def on_finish_level_set(lvl_set_results):
    print("GOT LEVEL SET RESULTS: ", lvl_set_results)
    # update the level row with the new info

    stats = []
    for lvl in lvl_set_results:
        stats.append(lvl['won_level'])

    print("performance:", sum(stats) / len(stats))


if __name__ == '__main__':
    sio.emit("connection")
    load_level_set(level_set)
