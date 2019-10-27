$(document).ready(function(){

    var received = $('#received');
    var devices = $('#socket_devices')

    var socket = new WebSocket("ws://localhost:8888/ws");
     
    socket.onopen = function(){  
      console.log("connected:"); 
      devices.append('<p>'+ socket + '</p>')
      console.log(devices)
      console.log(socket)
    }; 
 
    socket.onmessage = function (message) {
      console.log("receiving: " + message.data);
    //   received.empty()
      received.append(message.data);
      received.append($('<br/>'));

    };

    socket.onclose = function(){
      console.log("disconnected"); 
    };

    var sendMessage = function(message) {
      console.log("sending:" + message.data);
      socket.send(message.data);
    };


    // GUI Stuff
 
    // SCHEDULE send date to device
    $("#opt_send").click(function(ev){
      ev.preventDefault();
      var date = $('#select').val();
      sendMessage({ 'data' : date});
      console.log('clicked send')
      console.log(date)
      //$('#opt_val').val("")
    });
    // send a command to the serial port
    $("#cmd_send").click(function(ev){
      ev.preventDefault();
      var cmd = $('#cmd_value').val();
      sendMessage({ 'data' : cmd});
      $('#cmd_value').val("");
    });

    $('#clear').click(function(){
        console.log('clicked clear')
      received.empty();
    });


});
