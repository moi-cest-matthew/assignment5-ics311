from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum
import networkx as nx

class MessageType(Enum):
    PLAIN = "plain"
    RLE_COMPRESSED = "rle_compressed"
    FFT_COMPRESSED = "fft_compressed"
    ENCRYPTED = "encrypted"
    SIGNED = "signed"
    SIGN_CONFIRMATION = "sign_confirmation"

@dataclass
class Person:
    id: str
    public_key: Optional[bytes] = None
    private_key: Optional[bytes] = None
    
@dataclass
class MessageMetadata:
    message_type: MessageType
    original_length: Optional[int] = None  # For compressed messages
    compression_ratio: Optional[float] = None  # For FFT compression
    signature: Optional[bytes] = None  # For signed messages
    original_hash: Optional[bytes] = None  # For signed messages
    additional_data: Optional[Dict[str, Any]] = None

@dataclass
class Message:
    sender: Person
    receiver: Person
    metadata: MessageMetadata
    body: str

class CommunicationNetwork:
    def __init__(self):
        self.graph = nx.Graph()
        self.people: Dict[str, Person] = {}
    
    def add_person(self, person: Person):
        self.people[person.id] = person
        self.graph.add_node(person.id)
    
    def add_connection(self, person1_id: str, person2_id: str):
        if person1_id in self.people and person2_id in self.people:
            self.graph.add_edge(person1_id, person2_id)
    
    def get_person(self, person_id: str) -> Optional[Person]:
        return self.people.get(person_id)
    
    def are_connected(self, person1_id: str, person2_id: str) -> bool:
        return nx.has_path(self.graph, person1_id, person2_id)
    
    def get_path(self, person1_id: str, person2_id: str) -> List[str]:
        if self.are_connected(person1_id, person2_id):
            return nx.shortest_path(self.graph, person1_id, person2_id)
        return []