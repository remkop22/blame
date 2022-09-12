# Blame
Reactive programming primitives using ~100 lines of Python.

## Usage

```python
from blame import Signal, Memo, effect, batch

# start out with a signal and an initial value.
count: Signal[int] = Signal(0)

# create some effect that reruns when the values it depends on are written.
# Read the inner value using Signal.get(self).
effect(lambda: print(f"count is: {count.get()}"))
# prints: count is: 0

count.set(10)
# prints: count is: 10

# create a derived value using a memo.
count_plus_one: Memo[int] = Memo(lambda: count.get() + 1)
# memo's can be read the same way.
effect(lambda: print(count_plus_one.get()))
# prints: 11

# effects can depend on multiple signals or memo's
message: Signal[str] = Signal("Hello world!")
print_message: Signal[bool] = Signal(False)
effect(lambda: print(message.get()) if print_message.get() else None)

# updates can be batched to dedup effects.
with batch():
  print_message.set(True)
  message.set("foo")
  message.set("bar")
# prints: bar

```
