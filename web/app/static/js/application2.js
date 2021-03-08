
$(document).ready(function(){

    function getTimeStemp(){
         var d = new Date($.now());
         var timeStemp = d.getFullYear().toString() +(d.getMonth()+1).toString() + d.getDate().toString() + d.getHours().toString() + d.getMinutes().toString() + d.getSeconds().toString();
         return timeStemp;
    }



    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    console.log("web url: "+ 'http://' + document.domain + ':' + location.port + '/test');
    console.log("room number: " + room);
    var numbers_received = [];
    //console.log(room)
    //receive details from server
    socket.emit('join',{"room":room});
    socket.on('newnumber', function(msg) {
        console.log("Received number" + msg.number);
        //maintain a list of ten numbers
        //if (numbers_received.length >= 10){
        //    numbers_received.shift()
        //}
        numbers_received.push(msg.number);
        var numbers_string = '';
        for (var i = 0; i < numbers_received.length; i++){
            //numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
            numbers_string = numbers_string  + "\n" + numbers_received[i].toString();
        }
        console.log(numbers_string);
        //$('textarea#log').val(numbers_string);

        var $textarea = $('#log');
        $textarea.val(numbers_string);
        $textarea.scrollTop($textarea[0].scrollHeight);


        //$('#log').html(numbers_string);
    });


    $("#btn1").click(function(){
      //alert("The paragraph was clicked.");
      var blob = new Blob([$('textarea#log').val()], {type: "text/plain"});
      url = window.URL.createObjectURL(blob);

      //var FileSaver = require('file-saver');
      //FileSaver.saveAs(blob, "hello world.txt");

      //console.log(url);
      //$(this).attr('href', url).attr('download', "log.txt");


      $("<a />", {
        download: "log" + room + "_" + getTimeStemp() + ".txt",
        ref:url
      })
      // append `a` element to `body`
      // call `click` on `DOM` element `a`
      .appendTo("body")[0].click();
      // remove appended `a` element after "Save File" dialog,
      // `window` regains `focus`
      $(window).one("focus", function() {
        $("a").last().remove()
      })



    });

});
