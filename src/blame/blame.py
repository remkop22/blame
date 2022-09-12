from typing import Callable, Dict, Generic, List, TypeVar 

class Context:

    def __init__(self):
        self.scopes = []
        self.batch: List[Dict[int, Scope]] = []

    def push(self, scope: 'Scope'):
        self.scopes.append(scope)

    def pop(self):
        self.scopes.pop()

    def subscribe(self, subscriptions):
        if self.scopes:
            self.scopes[-1].subscribe(subscriptions)

context = Context()

class Scope:

    def __init__(self, execute, *args, **kwargs):
        self._execute = execute
        self.dependencies: Dict[int, Dict[int, 'Scope']] = {} 
        self._args = args
        self._kwargs = kwargs

    def execute(self):
        self.cleanup()
        context.push(self)
        try:
            self._execute(*self._args, **self._kwargs)
        finally:
            context.pop()

    def subscribe(self, subscriptions: Dict[int, 'Scope']):
        subscriptions[id(self)] = self
        self.dependencies[id(subscriptions)] = subscriptions

    def cleanup(self):
        for dep in self.dependencies.values():
            del dep[id(self)]

        self.dependencies = {}

S = TypeVar('S')
class Signal(Generic[S]):

    def __init__(self, initial: S):
        self._subscriptions = {}
        self._value: S = initial

    def get(self) -> S:
        self.use()
        return self._value

    def use(self):
        context.subscribe(self._subscriptions)

    def leak(self) -> S:
        return self._value

    def set(self, value: S):
        self._value = value
        self.notify()

    def notify(self):
        if context.batch:
            for sub in [*self._subscriptions.values()]:
                context.batch[-1][id(sub)] = sub
        else:
            for sub in [*self._subscriptions.values()]:
                sub.execute()


M = TypeVar('M')
class Memo(Generic[M]):

    def __init__(self, func: Callable[..., M]):
        signal: Signal[M] = Signal(None) # type: ignore
        effect(lambda: signal.set(func()))
        self._signal: Signal[M] = signal

    def get(self) -> M:
        return self._signal.get()


def effect(func: Callable, *args, **kwargs):
    Scope(func, *args, **kwargs).execute()


class BatchContext:

    def __enter__(self):
        context.batch.append({})

    def __exit__(self, *args, **kwargs):
        batch = context.batch.pop()
        for scope in batch.values():
            scope.execute()


def batch() -> BatchContext:
    return BatchContext()

