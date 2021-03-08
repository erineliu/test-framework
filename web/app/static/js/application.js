
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/cmd' );
    console.log("web url: "+ 'http://' + document.domain + ':' + location.port + '/cmd' );
    socket.on('connect', function() {
        //console.log("socket.id");
        socket.emit('connect_event', {data: 'connected!'});
    });


    socket.on('server_response', function(msg) {
        $('#output').append(msg.data+"\n").html();
    });


    socket.on('cmd_finish_response', function() {
        $('button#execute').text('Execute');
        $('button#execute').prop('disabled', false);
    });



    $('form#emit').submit(function(event) {

        $('button#execute').html('<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>run...');
        $('button#execute').prop('disabled', true);

        //$("button#execute").text('Run ...');
        //$('button#execute').prop('disabled', true).text('Run ...');
        $('#output').empty();
        socket.emit('client_event', {user: $('#user').val(),cmd:$('#cmd').val(),pwd:$('#pwd').val(),ip:$('#ip').val()});
        return false;
    });

});
