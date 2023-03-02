var pengirim = '';
var ws = new WebSocket("ws://localhost:8000/ws");
ws.onmessage = function(event){
    var messages = document.getElementById("messages")
    var message = document.createElement("li")
    message.style = 'list-style:None;';
    let data = event.data;
    var msg = data.split('-');
    message.innerHTML = '<div class="card"><h5 class="card-header">'+pengirim+'</h5><div class="card-body"><p class="card-text">'+msg[0]+'</p></div></div></br>';
    messages.appendChild(message)

};

function kirimpesan(event){
    var prm = document.getElementById("pengirim")
    var psn = document.getElementById("pesan")
    pengirim = prm.value
    ws.send(psn.value+'-'+pengirim)
    psn.value = ''
    event.preventDefault();
}