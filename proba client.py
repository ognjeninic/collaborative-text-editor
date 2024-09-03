import asyncio
import websockets
import json
import tkinter as tk
from tkinter import simpledialog, messagebox
import threading
import time
import logging

my_address = ""
logging.basicConfig(level=logging.DEBUG)

# Function to handle receiving updates from the server
async def listen_for_updates(text_widget, uri, doc_id_var):
    while True:
        try:
            async with websockets.connect(uri, timeout=5) as websocket:
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)

                        # Handle document updates
                        if data['type'] == 'update':
                            if data['remote_address'] != my_address:
                                cursor_position = text_widget.index(tk.INSERT)
                                text_widget.delete('1.0', tk.END)
                                text_widget.insert(tk.END, data['content'])
                                try:
                                    text_widget.mark_set(tk.INSERT, cursor_position)
                                except tk.TclError:
                                    text_widget.mark_set(tk.INSERT, tk.END)

                        # Handle metadata updates
                        elif data['type'] == 'metadata':
                            doc_id = select_document(data['documents'])
                            my_address = data['remote_address']
                            doc_id_var.set(doc_id)

                            await websocket.send(json.dumps({
                                'type': 'view',
                                'doc_id': doc_id
                            }))

                        # Handle save notifications
                        elif data['type'] == 'saved':
                            print("saved")
                            #messagebox.showinfo("Info", data['message'])

                    except websockets.exceptions.ConnectionClosed:
                        print("Connection closed, reconnecting")
                        break
                    except Exception as e:
                        print(f"Error receiving update: {e}")
                        break

        except (websockets.exceptions.ConnectionClosedError, ConnectionRefusedError):
            print("Connection failed, retrying in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Error in listen_for_updates: {e}")
            await asyncio.sleep(5)


edit_sent = False

# Function to handle sending edits to the server
async def send_edit(text_widget, uri, doc_id_var):
    global edit_sent
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                previous_content = text_widget.get('1.0', tk.END).rstrip('\n')
                while True:
                    try:
                        current_content = text_widget.get('1.0', tk.END).rstrip('\n')
                        # Check if the content has changed and an edit hasn't been sent
                        if current_content != previous_content and not edit_sent:
                            doc_id = doc_id_var.get()
                            if doc_id:
                                await websocket.send(json.dumps({
                                    'type': 'edit',
                                    'doc_id': doc_id,
                                    'content': current_content,
                                    'remote_address': my_address
                                }))
                                # Update previous_content and set the flag
                                previous_content = current_content
                                edit_sent = True
                        else:
                            # Reset the flag if the content is the same
                            edit_sent = False
                        await asyncio.sleep(0.1)
                    except websockets.exceptions.ConnectionClosed:
                        print("Connection closed, reconnecting")
                        break
                    except Exception as e:
                        print(f"Error sending edit: {e}")
                        break
        except Exception as e:
            print(f"Error connecting to websocket: {e}")

        except (websockets.exceptions.ConnectionClosedError, ConnectionRefusedError):
            print("Connection failed, retrying in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Error in send_edit: {e}")
            await asyncio.sleep(5)

# Function to select a document based on metadata
def select_document(documents):
    doc_list = "\n".join(f"{doc_id}: {name}" for doc_id, name in documents.items())
    print(doc_list)
    
    return "1"

# Function to start the asyncio event loop
def start_asyncio_loop(loop):
    try:
        loop.run_forever()
    except asyncio.CancelledError:
        pass

# Main function to run the client
def run_client():
    root = tk.Tk()
    text_widget = tk.Text(root)
    text_widget.pack(expand=True, fill=tk.BOTH)

    uri = "ws://10.61.1.112:6789"
    doc_id_var = tk.StringVar()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Start listening and sending tasks
    loop.create_task(listen_for_updates(text_widget, uri, doc_id_var))
    loop.create_task(send_edit(text_widget, uri, doc_id_var))

    # Event to handle shutdown
    shutdown_event = threading.Event()
    
    def on_shutdown():
        print("Shutting down...")
        root.destroy()

        # Cancel all tasks and stop the event loop
        for task in asyncio.all_tasks(loop):
            task.cancel()
        loop.call_soon_threadsafe(loop.stop)
        time.sleep(0.5)
        shutdown_event.set()

    root.protocol("WM_DELETE_WINDOW", on_shutdown)

    # Start the asyncio event loop in a separate thread
    asyncio_thread = threading.Thread(target=start_asyncio_loop, args=(loop,))
    asyncio_thread.start()
    root.mainloop()

    # Wait for shutdown to complete
    shutdown_event.wait()

    # Gracefully complete all tasks
    loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop), return_exceptions=True))
    loop.stop()
    asyncio_thread.join()
    loop.close()

if __name__ == "__main__":
    run_client()

