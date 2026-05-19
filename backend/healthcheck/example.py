from typing import Optional

from healthcheck import AbstractServiceHealthChecker


class ExampleHealthChecker(AbstractServiceHealthChecker):
    def __init__(self, example_dependency: Optional[str] = None):
        self.example_dependency = example_dependency

    async def check_health(self):
        # NOTE: Put the actual health check logic here.
        pass
