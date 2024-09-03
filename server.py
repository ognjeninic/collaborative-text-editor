import asyncio
import websockets
import json
import os
from collections import defaultdict
import logging


logging.basicConfig(level=logging.DEBUG)

# Document state: {doc_id: {'content': '', 'version': 0, 'name': 'document_name'}}
documents = defaultdict(lambda: {'content': '', 'version': 0, 'name': ''})
# Metadata: {doc_id: 'document_name'}
metadata = {}

# Set of connected clients: {websocket: doc_id}
clients = {}

# Path to save documents
save_path = "documents"
metadata_file = f"{save_path}\metadata.json"

# Ensure the save directory exists
os.makedirs(save_path, exist_ok=True)


def load_documents():
    global documents, metadata
    # Load metadata
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            print(f"OTVOREN METADATA.JSON\n{metadata}")
    else:
        metadata = {}

    # Load document content based on metadata
    for doc_id in metadata:
        file_path = os.path.join(save_path, f"{doc_id}.txt")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            documents[doc_id]['content'] = content
            documents[doc_id]['version'] = 1
            documents[doc_id]['name'] = metadata[doc_id]

load_documents()

# Function to save a document to a file after it goes idle for 2 seconds
async def save_document(doc_id):
    file_path = os.path.join(save_path, f"{doc_id}.txt")
    with open(file_path, 'w') as f:
        f.write(documents[doc_id]['content'])

    # Notify all clients viewing this document that it has been saved
    await broadcast_to_doc(doc_id, json.dumps({
        'type': 'saved',
        'doc_id': doc_id,
        'message': f"Document '{documents[doc_id]['name']}' has been saved."
    }))

# Broadcast a message to all clients viewing a specific document
async def broadcast_to_doc(doc_id, message):
    to_remove = set()
    for websocket, viewed_doc_id in clients.items():
        if viewed_doc_id == doc_id:
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                to_remove.add(websocket)

    for websocket in to_remove:
        del clients[websocket]

# Function to handle incoming connections and messages
async def handler(websocket, path):
    # Register the new client without a specific document initially
    clients[websocket] = None

    # Send the metadata to the new client
    await websocket.send(json.dumps({
        'type': 'metadata',
        'documents': metadata,
        'remote_address': websocket.remote_address[0]
    }))
    print(metadata)
    print(f"VEBSOKET {websocket.remote_address}")

    try:
        async for message in websocket:
            data = json.loads(message)

            # Handling viewing a document
            if data['type'] == 'view':
                doc_id = data['doc_id']
                clients[websocket] = doc_id
                # Send the current content of the requested document
                await websocket.send(json.dumps({
                    'type': 'update',
                    'content': documents[doc_id]['content'],
                    'version': documents[doc_id]['version'],
                    'remote_address': websocket.remote_address[0]
                }))

            # Handling editing a document
            elif data['type'] == 'edit':
                doc_id = data['doc_id']
                documents[doc_id]['content'] = data['content']
                documents[doc_id]['version'] += 1
                await broadcast_to_doc(doc_id, json.dumps({
                    'type': 'update',
                    'content': documents[doc_id]['content'],
                    'version': documents[doc_id]['version'],
                    'remote_address': websocket.remote_address[0]
                }))
                # Schedule a save after 2 seconds of idle time
                asyncio.create_task(save_document(doc_id))

            # Handling creating a new document
            elif data['type'] == 'create':
                doc_id = data['doc_id']
                doc_name = data['name']
                documents[doc_id]['name'] = doc_name
                metadata[doc_id] = doc_name
                # Broadcast updated metadata to all clients
                await broadcast_to_doc(None, json.dumps({
                    'type': 'metadata',
                    'documents': metadata,
                    'remote_address': websocket.remote_address[0]
                }))
                
    finally:
        # Unregister the client on disconnect
        if websocket in clients:
            del clients[websocket]

print(metadata)
# Start the WebSocket server
start_server = websockets.serve(handler, "0.0.0.0", 6789)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


"""

document_state = {
    'content': '',
    'version': 0
}


# List of connected clients
clients = set()

async def handler(websocket, path):
    print("hendler")
    clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)

            if data['type'] == 'edit':
                document_state['content'] = data['content']
                document_state['version'] += 1

                await broadcast(json.dumps({
                    'type': 'update',
                    'content': document_state['content'],
                    'version': document_state['version']
                }))

    finally:
        # Unregister client
        clients.remove(websocket)

async def broadcast(message):
    # Send a message to all connected clients
    if clients:
        await asyncio.wait([client.send(message) for client in clients])

# Start the server
start_server = websockets.serve(handler, "localhost", 6789)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
"""