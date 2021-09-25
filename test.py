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

print({(1, 2, 3), (2, 3, 1)} == {(2, 3, 1), (1, 2, 3)})