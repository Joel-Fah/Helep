import os
import glob

breaker_pattern = '''class CircuitBreaker:
    def __init__(self, fail_threshold: int = 5, reset_after_s: float = 10.0):
        self.fail_threshold = fail_threshold
        self.reset_after_s = reset_after_s
        self.fails = 0
        self.opened_at: float | None = None

    def allow(self) -> bool:
        # TODO (student): implement open/half-open/closed state machine
        return True

    def record_success(self) -> None:
        self.fails = 0

    def record_failure(self) -> None:
        self.fails += 1'''

breaker_impl = '''import time

class CircuitBreaker:
    def __init__(self, fail_threshold: int = 5, reset_after_s: float = 10.0):
        self.fail_threshold = fail_threshold
        self.reset_after_s = reset_after_s
        self.fails = 0
        self.opened_at: float | None = None

    def allow(self) -> bool:
        if self.fails >= self.fail_threshold:
            if self.opened_at and (time.time() - self.opened_at) > self.reset_after_s:
                return True
            return False
        return True

    def record_success(self) -> None:
        self.fails = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.fails += 1
        if self.fails >= self.fail_threshold and self.opened_at is None:
            self.opened_at = time.time()'''

for file in glob.glob('services/*/app/events.py'):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if breaker_pattern in content:
        new_content = content.replace(breaker_pattern, breaker_impl)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {file}')
    else:
        print(f'Pattern not found in {file}')
