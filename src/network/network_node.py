from graph import Node


class NetworkNode(Node):
    def __init__(self, id: str, resources: set[str]):
        super().__init__(id)
        self.resources = resources

    def has_resource(self, resource: str) -> bool:
        return resource in self.resources
