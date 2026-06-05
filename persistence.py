

import json
import os
from data_structures import LinkedList, Stack

def save_state(path, user_histories, user_positions, user_undo_stacks, last_activity):
    data = {
        "histories": {uid: ll.to_list() for uid, ll in user_histories.items()},
        "positions": user_positions,
        "undo": {uid: dump_stack(st) for uid, st in user_undo_stacks.items()},
        "last_activity": last_activity,
    }
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def load_state(path):
    state = {
        "histories": {},
        "positions": {},
        "undo": {},
        "last_activity": {},
    }
    if not os.path.exists(path):
        return state

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for uid, cmds in data.get("histories", {}).items():
        ll = LinkedList()
        for cmd in reversed(cmds):
            ll.push_front(cmd)
        state["histories"][uid] = ll

    state["positions"] = data.get("positions", {})

    for uid, items in data.get("undo", {}).items():
        st = Stack()
        for item in items: 
            st.push(item)
        state["undo"][uid] = st

    state["last_activity"] = data.get("last_activity", {})

    return state


def dump_stack(stack):
    items = []
    temp = Stack()
    while not stack.is_empty():
        v = stack.pop()
        items.append(v)
        temp.push(v)
    while not temp.is_empty():
        stack.push(temp.pop())
    return items
