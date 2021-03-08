var roomID;
var clientID;
var SN;
var project;
var script;
var curTestCase;
var curTestSeqNum;
var projetlist = [];
var startFlag=0;
var msgBackFlag = 1;
var lockFlag = 0;

$(window).on('load', function(){

    //alert("onload");
    //$('.selectpicker').selectpicker('refresh');
    //$('.selectpicker').selectpicker('val'," ");

});





$(function() {
  $(".selectpicker").selectpicker({
    noneSelectedText : "Project Select"
  });
});


function activaTab(tab){
    $('.nav-tabs a[href="#' + tab + '"]').removeClass("disabled");
    $('.nav-tabs a[href="#' + tab + '"]').tab('show');

};


function startCount(preTime){

    var sec = preTime;
    function pad ( val ) { return val > 9 ? val : "0" + val; }
    conuter = setInterval( function(){
        $("#secondsValue").html(pad(++sec%60));
        $("#minutesValue").html(pad(parseInt((sec % 3600)/60,10)));
        $("#hoursValue").html(pad(parseInt(sec/3600,10)));
    }, 1000);

};


function stopCount(){
    clearInterval(conuter);
};



function clearCount(){
    $("#secondsValue").html("00");
    $("#minutesValue").html("00");
    $("#hoursValue").html("00");
};


function blinkText(selecter){
    stateFade = setInterval(function blink_text() {
        $(selecter).fadeOut(500);
        $(selecter).fadeIn(1000);
    },1500);
};


function stopBlinkText(selecter){
    clearInterval(stateFade);
    $(selecter).finish();
};




function saveLock(){

    var dataJSON={"roomID":roomID,"name":user_name};

    $.ajax({
        type : 'post',
        data: JSON.stringify(dataJSON),
        url : 'http://' + document.domain + ':' + location.port + '/save_lock',
        contentType: 'application/json',
        success : function(data) {
        }
    });
};



function releaseLock(){

    var dataJSON={"roomID":roomID,"name":user_name};

    $.ajax({
        type : 'post',
        data: JSON.stringify(dataJSON),
        url : 'http://' + document.domain + ':' + location.port + '/release_lock',
        contentType: 'application/json',
        success : function(data) {
        }
    });

};



function runTest(){

    var dataJSON={"roomID":roomID,"SN":SN,"project":project,"script":script};

    $.ajax({
        type : 'post',
        data: JSON.stringify(dataJSON),
        url : 'http://' + document.domain + ':' + location.port + '/run_test',
        contentType: 'application/json',
        success : function(data) {
        }
    });
};


function stopTest(){

    var dataJSON={"roomID":roomID};

    $.ajax({
        type : 'post',
        data: JSON.stringify(dataJSON),
        url : 'http://' + document.domain + ':' + location.port + '/stop_test',
        contentType: 'application/json',
        success : function(data) {
        }
    });
};


function getTime(){
    //console.log(new Date() / 1000);
    //console.log(new Date());
    //return Math.round(new Date() / 1000);
    return Date.now();
}


function startTimeStamp(){

    var startTime = getTime();
    console.log(startTime);
    var dataJSON={"startTime":startTime};


    $.ajax({
        type : 'post',
        data: JSON.stringify(dataJSON),
        url : 'http://' + document.domain + ':' + "60002"  + '/startTimeStamp/test123',
        contentType: 'application/json',
        success : function(data) {
        }

    });


};


function stopTimeStamp(){
    var stopTime = getTime();
    var dataJSON={"stopTime":stopTime};

    $.ajax({
        type : 'post',
        data: JSON.stringify(dataJSON),
        url : 'http://' + document.domain + ':' + "60002"  + '/stopTimeStamp/test123',
        contentType: 'application/json',
        success : function(data) {
        }
    });
};


function updateState(state){

    var dataJSON={ "state":state};
    console.log(state);

    $.ajax({
        type : 'post',
        data: JSON.stringify(dataJSON),
        url : 'http://' + document.domain + ':' + "60002"  + '/updateState/test123',
        contentType: 'application/json',
        success : function(data) {
        }
    });
};

function clearDBdata(){

     $.ajax({
        type : 'post',
        url : 'http://' + document.domain + ':' + "60002"  + '/clear_table/test123',
        contentType: 'application/json',
        success : function(data) {
        }
    });

};


function getMesgFromDataBase(){
    //dataType: 'jsonp',
    //headers: {
    //        'Access-Control-Allow-Origin': '*',
    //        'Content-Type':'application/json'
    //    },
    // },

    $.ajax({
        timeout: 5000,
        type : 'GET',
        url : 'http://' + document.domain + ':' + "60002" + '/get_mesg/test123',
        dataType : 'jsonp',
        jsonp: 'callback',
        jsonpCallback: "successCallback",
        success : function(data) {

            if (data.length != 0){
                activaTab("profile");
            }

            var numbers_string = '';
            for (var i = 0; i < data.length; i++){
                //console.log(data[i]["mesg"]);
                //$('#output').append(data[i]["mesg"]+"\n");
                numbers_string = numbers_string  + data[i]["mesg"] + "\n";
            }


            $("#output").append(numbers_string).trigger('change');;
            //alert($("#output")[0].scrollHeight);


            $("#output").scrollTop($("#output")[0].scrollHeight);

            msgBackFlag=1;

        },
        error: function(mesg) {
            console.log('Request Error.'+mesg);
        }
    });


};



function getTestCaseFromDataBase(){
    $.ajax({
        timeout: 5000,
        type : 'GET',
        url : 'http://' + document.domain + ':' + "60002" + '/get_testCase/test123',
        dataType : 'jsonp',
        jsonp: 'callback',
        jsonpCallback: "successCallback2",
        success : function(data) {
            for (var i = 0; i < data.length; i++){
                //console.log(data[i]);
                $("#testCaseTable tbody").append("<tr> <th scope='row'>" + data[i]["pid"] + "</th>" + "<td>"+ data[i]["name"] + "</td>" + "</tr>");
                updateTestCaseStatus(data[i]["pid"],data[i]["status"]);
            }

        },
        error: function(mesg) {
            console.log('Request Error.'+mesg);
        }

    });

};


function getLockFromDataBase(){
    $.ajax({
        timeout: 5000,
        type : 'GET',
        url : 'http://' + document.domain + ':' + "60002" + '/getLock/' + roomID,
        dataType : 'jsonp',
        jsonp: 'callback',
        jsonpCallback: "successCallback4",
        success : function(data) {

            if( data.length == 0 ){
               return;
            }

            var lucker_dB = data[0]["name"];

            if( lucker_dB == "" ){
               return;
            }

           lockAction(lucker_dB);

        },
        error: function(mesg) {
            console.log('Request Error.'+mesg);
        }

    });
};





function getInfoFromDataBase(){
    $.ajax({
        timeout: 5000,
        type : 'GET',
        url : 'http://' + document.domain + ':' + "60002" + '/get_info/test123',
        dataType : 'jsonp',
        jsonp: 'callback',
        jsonpCallback: "successCallback3",
        success : function(data) {
            if (data.length == 0){
                return;
            }

            SN = data[0]["sn"];
            updateInfo(data[0]["stage"],data[0]["OPID"],data[0]["IP"],data[0]["testMode"],data[0]["sn"]);
            updateRunState(data[0]["state"],data[0]["project"],data[0]["startTime"],data[0]["endTime"]);

        },
        error: function(mesg) {
            console.log('Request Error.'+mesg);
        }

    });

};



function lockAction(locker){

    $("#lock").find("span").removeClass('fa-unlock').addClass("fa-lock");


    if (user_name != locker ){

        $("#lock").addClass("btn-danger");
        $("#lock").prop('disabled', true);
        $("#lock").attr("title", "Locker: " + locker );

        $("#OK").prop('disabled', true);
        $("#run").prop('disabled', true);
        $("#reset").prop('disabled', true);

    }

}


function unLockAction(){

    $("#lock").find("span").removeClass('fa-lock').addClass("fa-unlock");
    $("#lock").removeClass("btn-danger");
    $("#lock").prop('disabled', false);
    $("#lock").removeAttr("title");

    $("#run").prop('disabled', false);
    $("#reset").prop('disabled', false);

}






function updateStartTime(startTime){
    var curTime = getTime();
    //startCount((curTime-startTime));
    startCount( Math.round((curTime-startTime) / 1000));
}


function updateEndTime(sec){

    function pad ( val ) { return val > 9 ? val : "0" + val; }
    $("#secondsValue").html(pad(sec%60));
    $("#minutesValue").html(pad(parseInt((sec % 3600)/60,10)));
    $("#hoursValue").html(pad(parseInt(sec/3600,10)));

}


function updateTestState(state,startTime,endTime){

    if (state == "Testing"){
        $("#stateBoard").removeClass('text-danger').addClass( "bg-white text-primary" ).text("TEST");
        blinkText("#stateBoard");
        $("#run").text("Stop").addClass( "btn-danger" );
        updateStartTime(startTime);
        startFlag=1;
    }

    else if (state == "PASS" ){
        $("#stateBoard").addClass( "bg-white text-success" ).text("PASS");
    }


    else if (state == "FAIL"){
        $("#stateBoard").addClass( "bg-white text-danger" ).text("FAIL");
        updateEndTime(Math.round((endTime - startTime)/1000));
    }


    else if (state == "STOP"){
        $("#stateBoard").addClass( "bg-white text-danger" ).text("STOP");
        updateEndTime(Math.round((endTime - startTime)/1000));
    }

}

function updateProjetState(project){
    $('.selectpicker').selectpicker('val', jQuery.inArray(project,projetlist)).trigger("change");
    $("#selProj").prop('disabled', true);
    $('#selProj').selectpicker('refresh');
    $("#OK").prop('disabled', true);
}




function updateRunState(state,project,startTime,endTime){
    updateProjetState(project);
    updateTestState(state,startTime,endTime);
}



function updateInfo(stage,OPID,IP,testMode,SN){
    $("#testStage").text(stage);
    $("#testOPID").text(OPID);
    $("#testIP").text(IP);
    $("#testMode").text(testMode);
    $("#testSN").text(SN);
}


function updateTestCaseStatus(SeqNum,result){
    var tr = $('#testCaseTable  tr');
    if (result == "PASS"){
        var TableClass = "table-success";
    }
    else if (result == "FAIL"){
        var TableClass = "table-danger";

    }
    else if (result == "Testing"){
        var TableClass = "table-primary";
    }
    else{
        return;
    }

    $(tr[SeqNum -1]).addClass(TableClass);
}


function scrollToLine($textarea, lineNumber) {
    var lineHeight = parseInt($textarea.css('line-height'));
    $textarea.scrollTop(lineNumber * lineHeight);
}

$(document).ready(function($){
    // ## set variable ##
    var pData;
    var conuter;
    var stateFade;

    //###################

    console.log("dddd" + user_role);


    $('#myLoginModal').on('shown.bs.modal', function () {
        $('#myLoginModal input:visible:first').first().focus();
    });



    // ## show lock icon ##
    if ( user_role == "" ){
        $("#lock").hide();
    }




    $("#output").on('change', function() {

    });


    $(window).bind("beforeunload", function() {
        socket.emit('disconnect_event',{"roomID": roomID,"clientID": clientID});

    });


    roomID = $(location).attr("href").split('/').pop();

    //var socket = io.connect('http://' + document.domain + ':' + location.port + '/cmd' );
    //console.log("socket url: "+ 'http://' + document.domain + ':' + location.port + '/cmd' );
    var socket = io.connect('http://' + document.domain  + '/cmd' );
    console.log("socket url: "+ 'http://' + document.domain + '/cmd' );
    console.log(socket)

    socket.on('connect', function() {

        getLockFromDataBase();
        getInfoFromDataBase();
        getMesgFromDataBase();
        getTestCaseFromDataBase();

        var clientIDInfo = socket.id;
        clientID = clientIDInfo.split("#")[1];
        console.log(clientID);
        socket.emit('connect_event',{"roomID": roomID,"clientID": clientID});
    });


    socket.on('disconnect', function() {

    });


    socket.on("manual_update",function(msg){

        console.log(msg["action"]);

        if (msg["action"] == "STOP"){

            $("#run").text("Run").removeClass('btn-danger').addClass("btn-secondary");
            stopBlinkText("#stateBoard");
            stopCount();
            stopTimeStamp();
            $("#stateBoard").addClass( "text-danger" ).text("STOP");
            startFlag = 0;

        }
        else if(msg["action"] == "Testing"){

            $("#output").text('');
            $("#run").text("Stop").addClass( "btn-danger" );
            $("#stateBoard").removeClass('text-danger').addClass( "bg-white text-primary" ).text("TEST");
            blinkText("#stateBoard");
            startCount(0);
            startTimeStamp();
            startFlag = 1;

        }

        else if(msg["action"] == "Lock"){

            lockAction(msg["locker"]);

        }
        else if(msg["action"] == "unLock"){

            unLockAction();
            releaseLock();

        }
        else if(msg["action"] == "mesgBox"){
            $('#myModal').modal('hide');
        }

    });


    socket.on('mesg_box', function(msg) {
        console.log("Received:" + msg);
        console.log("Received:" + msg.image);

        var title = curTestSeqNum + ". " + curTestCase
        $("#myModal .modal-header #exampleModalLongTitle").text(title);
        $("#myModal .modal-body .row:first p").text(msg.text);
        console.log(msg.image);
        $("#myModal .modal-body #image").attr("src",msg.image);
        $('#myModal').modal('show');

    });

    socket.on('mesg_box_close', function() {
         $('#myModal').modal('hide');
    });


    $("#mesgBoxYes").click(function(){
        console.log("yes123");
        socket.emit('mesg_box_return', {"data":true,"roomID": roomID});
        socket.emit('manualChange',{"roomID": roomID,"action":"mesgBox","result":"yes"});
    });



    $("#mesgBoxNo").click(function(){
        console.log("no123");
        socket.emit('mesg_box_return', {"data":false,"roomID": roomID});
        socket.emit('manualChange',{"roomID": roomID,"action":"mesgBox","result":"no"});
    });


    var mesg_list=[];
    var j=0;
    socket.on('mesg_output', function(msg) {
        console.log("Received:" + msg.output);
        var $textarea = $('#output');

        mesg_list.push(msg.output);
        console.log(msgBackFlag);
        console.log(mesg_list.length);
        if(msgBackFlag == 1){

            /*
            var numbers_string = '';
            for (var i = 0; i < mesg_list.length; i++){
                numbers_string = numbers_string  + "\n" + mesg_list[i];
            }
            $textarea.append(numbers_string);
            */

            for (var i = 0; i < mesg_list.length; i++){
                $textarea.append(mesg_list[i]+"\n");
            }

            $textarea.scrollTop($textarea[0].scrollHeight);

            if (mesg_list.length != 0){
                mesg_list.splice(0, mesg_list.length);
            }
            //j= mesg_list.length
        }


    });




    socket.on('test_end', function(msg){
        $("#run").text("Run").removeClass('btn-danger').addClass("btn-secondary");
        stopTest();
        startFlag = 0;
    });



    socket.on('stage_Initial', function(msg){
        $("#output").text('');
        $("#stateBoard").removeClass('text-danger  text-success').addClass( "bg-white text-primary" ).text("TEST");
        startCount(0);
        blinkText("#stateBoard");
        startTimeStamp();
    });



    socket.on('state_update', function(msg) {
        //console.log(msg.update_dutInfo.stage);
        if ("update_dutInfo" in msg){
            $("#testStage").text(msg.update_dutInfo.stage);
            $("#testOPID").text(msg.update_dutInfo.OPID);
            $("#testIP").text(msg.update_dutInfo.IP);
            $("#testMode").text(msg.update_dutInfo.testMode);

        }

        if ("add_testCaseList" in msg){
            var testCaseList = msg.add_testCaseList;
            //console.log(testCaseList.length)
            $("#testCaseTable tbody").html("");
            for (var i = 0; i < testCaseList.length; i++){
                var cur_jq = jQuery.parseJSON(testCaseList[i]);
                //console.log(cur_jq.seqNum);
                //$('.list-group').append("<li class='list-group-item list-group-item-action text-truncate'>" + cur_jq.name + "</li>");
                //$('.list-group').append("<li class='list-group-item list-group-item-action'>" + cur_jq.name + "</li>");
                $("#testCaseTable tbody").append("<tr> <th scope='row'>" + cur_jq.seqNum + "</th>" + "<td>"+ cur_jq.name + "</td>" + "</tr>");
            }
        }


        if ("case_start" in msg){
            console.log(msg.case_start.name);
            curTestCase = msg.case_start.name;
            curTestSeqNum = msg.case_start.SeqNum;

            var tr = $('#testCaseTable  tr');
            //$(tr[msg.case_start.SeqNum -1]).css("background-color", "lightgreen");
            if (msg.case_start.SeqNum > 1){
                $(tr[msg.case_start.SeqNum -2]).removeClass("table-primary");
            }
            $(tr[msg.case_start.SeqNum -1]).addClass("table-primary");

        }


        if ("case_result" in msg){

            var tr = $('#testCaseTable  tr');
            if (msg.case_result.result == "PASS"){
                var TableClass = "table-success";
            }
            else{
                var TableClass = "table-danger";
            }

            $(tr[msg.case_result.SeqNum -1]).addClass(TableClass);
        }



        if ("stage_result" in msg){



            /*
            //$("#run").click();
            $("#run").text("Run").removeClass('btn-danger').addClass("btn-secondary");
            stopBlinkText("#stateBoard");
            stopCount();
            stopTimeStamp();
            stopTest();
            startFlag = 0;
            */

            stopBlinkText("#stateBoard");
            stopCount();
            stopTimeStamp();

            var stage_result = msg.stage_result.result;
            if (stage_result == "PASS" ){
                $("#stateBoard").addClass( "text-success" ).text(msg.stage_result.result);
            }
            else{
                $("#stateBoard").addClass( "text-danger" ).text(msg.stage_result.result);
                $("#run").text("Run").removeClass('btn-danger').addClass("btn-secondary");
                stopTest();
                startFlag = 0;
            }

        }


    });



    //## <SN input> press enter key ##
    $('#SN').keypress(function(event){
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if(keycode == '13'){
            //alert('You pressed a "enter" key in textbox');
            SN = $(this).val();
            $("#testSN").text(SN);
            $(this).prop('disabled', true);
            activaTab("profile");

        }
        //Stop the event from propogation to other handlers
        //If this line will be removed, then keypress event handler attached
        //at document level will also be triggered
        event.stopPropagation();
    });


    $("#lock").click(function() {

        if (lockFlag == 0){
            $(this).find("span").removeClass('fa-unlock').addClass("fa-lock");
            saveLock();
            lockFlag = 1;
            socket.emit('manualChange',{"roomID": roomID,"action":"Lock","locker":user_name});
        }else
        {
            $(this).find("span").removeClass('fa-lock').addClass("fa-unlock");
            releaseLock();
            lockFlag = 0;
            socket.emit('manualChange',{"roomID": roomID,"action":"unLock"});
        }

    });


    $( "#OK" ).click(function() {


        if($("#selProj").val() == null){
            return;
        }

        $(this).prop('disabled', true);
        $("#selProj").prop('disabled', true);
        $('#selProj').selectpicker('refresh');

        activaTab("home");
        $('#SN').prop('disabled', false).val("");
        setTimeout(function() { $('input[name="SN"]').select() }, 300);

    });


    $( "#run" ).click(function() {
        if( startFlag == 0 ){
            $("#output").text('');

            $("#run").text("Stop").addClass( "btn-danger" );
            $("#stateBoard").removeClass('text-danger  text-success').addClass( "bg-white text-primary" ).text("TEST");
            blinkText("#stateBoard");
            startCount(0);
            startTimeStamp();

            startFlag = 1;

            runTest();
            clearDBdata();
            socket.emit('manualChange',{"roomID": roomID,"action":"Testing"});


        }

        else if( startFlag == 1 ){


            $("#run").text("Run").removeClass('btn-danger').addClass("btn-secondary");
            $("#stateBoard").addClass( "text-danger" ).text("STOP");
            stopBlinkText("#stateBoard");
            stopCount();
            stopTimeStamp();
            startFlag = 0;

            stopTest();
            updateState("STOP");
            socket.emit('manualChange',{"roomID": roomID,"action":"STOP"});

        }

    });



    $( "#reset" ).click(function() {
        //$('.nav-tabs a[href="#home"]').tab('show');
        activaTab("home");
        $('#SN').prop('disabled', false).val("");
        //$('#SN')[0].focus();
        setTimeout(function() { $('input[name="SN"]').select() }, 300);
    });


    $('#selProj').on('change', function(e){
        //console.log(this.value);


        $('#scriptPath').text(pData.results[this.value].testFlow);
        script = pData.results[this.value].testFlow;
        project = pData.results[this.value].name;
    });

    //console.log("sssss" + $SCRIPT_ROOT);

    $.ajax({
        type : 'get',
        url : 'http://' + document.domain + ':' + location.port + '/add_numbers',
        dataType : 'json',
        success : function(data) {//返回list資料並迴圈獲取
          pData = data;
          var select = $("#selProj");
          for (var i = 0; i <data.results.length; i ++ ) {
            //select.append('<option value="' +  data.results[i].ROAD_KEY + '">' +  data.results[i].ROAD_VALUE + "</option>");

            select.append('<option value="' + i + '">' +  data.results[i].name + "</option>");
            projetlist.push(data.results[i].name);

          }
          //$('.selectpicker').selectpicker('refresh');
          $('.selectpicker').selectpicker('val',"");
          $('.selectpicker').selectpicker('refresh');

        }
    });


    $( "#testCaseTable tbody" ).on("click","tr",function() {
        //var currentRow=$(this).closest("tr");
        //console.log(currentRow.find("td:eq(0)").text());
        var testCaseSeq = $(this).find("th").eq(0).html();
        var testCaseName = $(this).find("td").eq(0).html();
        var search_str = "Test Case  : " + testCaseSeq + " - " + testCaseName;
        var mesg_out = $('#output').val();
        if (mesg_out.lastIndexOf(search_str) != -1 ){
            var line = mesg_out.substr(0, mesg_out.lastIndexOf(search_str)).split("\n").length-1;
            scrollToLine($('#output'),line);
        }
    });



    $( "div.row" ).sortable({
	    connectWith: ".row",
        handle: ".card-header",
        placeholder: "card-placeholder",
        start: function(e, ui){
            ui.placeholder.width(ui.item.find('.card').width());
            ui.placeholder.height(ui.item.find('.card').height());
            ui.placeholder.addClass(ui.item.attr("class"));
        }
    });

    $( "#cont1","#cont2" ).disableSelection();

    $('.card').on('mousedown', function(){
      $(this).css( 'cursor', 'move' );
    }).on('mouseup', function(){
      $(this).css( 'cursor', 'auto' );
    });;

    //$( "#draggable" ).draggable({ containment: "#cont1", scroll: false });
    //$( "#draggable1" ).draggable({ handle: "h5" });
    //$( "#draggable2" ).draggable();
    //$( "#dialog" ).dialog();
});

