
class Node:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next


class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def push_front(self, value):
        self.head = Node(value, self.head)
        self.size += 1

    def to_list(self):
        cur, out = self.head, []
        while cur:
            out.append(cur.value)
            cur = cur.next
        return out

    def clear(self):
        self.head = None
        self.size = 0

    def is_empty(self):
        return self.size == 0


class StackNode:
    def __init__(self, value, prev=None):
        self.value = value
        self.prev = prev


class Stack:
    def __init__(self):
        self.top = None
        self.size = 0

    def push(self, value):
        self.top = StackNode(value, self.top)
        self.size += 1

    def pop(self):
        if not self.top:
            return None
        v = self.top.value
        self.top = self.top.prev
        self.size -= 1
        return v

    def peek(self):
        return self.top.value if self.top else None

    def is_empty(self):
        return self.size == 0

    def clear(self):
        self.top = None
        self.size = 0


class QueueNode:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next


class Queue:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def enqueue(self, value):
        n = QueueNode(value)
        if not self.head:
            self.head = self.tail = n
        else:
            self.tail.next = n
            self.tail = n
        self.size += 1

    def dequeue(self):
        if not self.head:
            return None
        v = self.head.value
        self.head = self.head.next
        if not self.head:
            self.tail = None
        self.size -= 1
        return v

    def is_empty(self):
        return self.size == 0


class TreeNode:
    def __init__(self, node_id, prompt=None, conclusion=None):
        self.id = node_id
        self.prompt = prompt
        self.conclusion = conclusion
        # options: dict[str -> TreeNode]
        self.options = {}

    def add_option(self, key, child_node):
        self.options[key.strip().lower()] = child_node
