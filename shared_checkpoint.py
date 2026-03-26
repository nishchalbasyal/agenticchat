import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

# Shared database connection and checkpointer for all backends
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)
