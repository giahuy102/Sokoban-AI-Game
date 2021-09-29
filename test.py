# import time
# a = set()
# for i in range(500):
#     for j in range(500):
#         a.add((i, j))

# c = []
# start_time = time.time()
# for i in range(0, 200):
#     a.remove((200, i))
#     a.add((1001, i))
#     c.add(a.copy())
# print("--- %s seconds ---" % (time.time() - start_time))

# c = []
# a = list()
# for i in range(500):
#     for j in range(500):
#         a.add((i, j))

# start_time = time.time()
# for i in range(0, 200):
#     a[200] = (1001, i)
#     b = set(a)
#     c.add(b)
# print("--- %s seconds ---" % (time.time() - start_time))

# a = {(1, 2), (3, 4)}
# a.remove((1, 3))
# print(a)
# from queue import PriorityQueue

class Test:
    def __init__(self, priority):
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority

# q = PriorityQueue()


# ob1 = Test(1)
# ob2 = Test(2)

# q.put(ob1)
# q.put(ob2)
# q.put(Test(2))
# print(q.get().priority)
# print(q.get().priority)
# print(q.get().priority)

from queue import PriorityQueue


ob = PriorityQueue()
for i in range(10):
    ob.put(Test(2))
for i in range(11):
    ob.get()



