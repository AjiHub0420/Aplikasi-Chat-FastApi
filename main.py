from flask import Flask,render_template,url_for
from flask_sqlalchemy import SQLAlchemy
from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.wsgi import WSGIMiddleware
from typing import List,Optional

web = Flask(__name__)
web.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
web.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
web.app_context().push()
db = SQLAlchemy(web)
class Message(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))
    message = db.Column(db.String(50))

db.create_all()

@web.route("/")
def homepage():
    messages = Message.query.all()
    return render_template("index.html",messages=messages)


app = FastAPI()

class ConectManager:
    def __init__(self):
        self.active_connections:List[WebSocket] = []
    
    async def connect(self,websocket:WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self,websocket:WebSocket):
        self.active_connections.remove(websocket)
    
    async def personal_message(self,message:str,websocket:WebSocket):
        await websocket.send_text(message)

    async def broadcast_message(self,message:str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConectManager()

@app.websocket("/ws")
async def socketweb(websocket:WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg = str(data).split("-")
            # await manager.personal_message(f"You wrote: {msg[0]}",websocket)
            await manager.broadcast_message(f"{msg[1]} says: {data}")
            db.session.add(Message(name=msg[1],message=msg[0]))
            db.session.commit()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast_message(f"{msg[1]} has left the chat")
app.mount("/static",StaticFiles(directory="static"),name="static")
app.mount("",WSGIMiddleware(web))