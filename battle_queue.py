

class BattleQueueItem:
    duration = None
    relative_duration = None
    func = None

    def __init__(self, duration, func=None):
        if duration is not None and duration < 0:
            raise Exception("A SleeperItem may not have a duration below zero")
        self.duration = duration
        self.func = func

    def __str__(self):
        func_name = "None"
        if self.func is not None:
            func_name = str(self.func.__name__)

        return " - ".join([func_name, str(self.duration), str(self.relative_duration)])

    def run(self):
        if self.func is not None:
            self.func()

    def __lt__(self, other):
        a = self.duration if self.duration is not None else -1
        b = other.duration if other.duration is not None else -1
        return a < b


class BattleQueue:
    queue = None

    def __init__(self, queue=None):
        if queue is None:
            queue = []
        queue = sorted(queue)
        self.queue = queue

    def __str__(self):
        out = "SleeperQueue:"
        for i in self.queue:
            out += "\n" + str(i)
        return out

    def __add__(self, other):
        self.queue += other.queue
        self.queue = sorted(self.queue)
        return self

    def __bool__(self):
        return bool(self.queue)

    def activate(self):
        # Initial run (apply all with no delays)
        for i in self.queue:
            i.run()

        # Remove all with None duration
        for i in range(len(self.queue)):
            if self.queue[i].duration is not None:
                del self.queue[:i]
                break

        # set relative durations
        for i in range(len(self.queue)):
            if i > 0:
                self.queue[i].relative_duration = self.queue[i].duration - self.queue[i-1].duration
            else:
                self.queue[i].relative_duration = self.queue[i].duration

    def get_next_duration(self):
        if self.queue[0].relative_duration is None:
            return 0
        return self.queue[0].relative_duration

    def run_next(self, run_consecutive=False):
        # Empty case
        if not self.queue:
            return

        # Get and remove item
        item = self.queue[0]
        del self.queue[0]

        # Run item
        item.run()

        # Get index to insert item and re-adjust durations effected by insertion
        item.relative_duration = item.duration
        inserted_rd = None
        insert_index = None
        for i in range(len(self.queue)):
            if insert_index is None:
                if item.relative_duration - self.queue[i].relative_duration > 0:
                    item.relative_duration -= self.queue[i].relative_duration
                else:
                    insert_index = i
                    inserted_rd = item.relative_duration
            if insert_index is not None:
                if self.queue[i].relative_duration == 0:
                    break
                self.queue[i].relative_duration -= inserted_rd

        # Insert item
        if insert_index is not None:
            self.queue.insert(insert_index, item)
        else:
            self.queue.append(item)

        # Run all that should be run at the same time
        if run_consecutive and self.get_next_duration() == 0:
            self.run_next(run_consecutive=True)


def main():
    item_set = [
        BattleQueueItem(1000),
        BattleQueueItem(600),
        BattleQueueItem(None),
        BattleQueueItem(750)
    ]

    queue = BattleQueue(item_set)
    print("\n0 - " + str(queue))
    queue.activate()
    print("\n0 - " + str(queue))
    for i in range(30):
        queue.run_next()
        print("\n" + str(i+1) + " - " + str(queue))


if __name__ == "__main__":
    main()
