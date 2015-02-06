var address="http://localhost:5000";
var session="";
var user="";
var cache="";
var revision=0;
var interval=undefined;

function newSession(){
    $.getJSON(address + "/new", function(data) {
        if(data["status"] == "ok") {
            user=data["uid"];
            session=data["sid"];
            console.log("/new got user " + user + " with session " + session);
            interval = window.setInterval(push, 1000);
        } else {
            console.log("/new got fail");
        }
    });
}

function joinSession(){
    tokencode = prompt("Enter the token code from the other device here").split(":")
    $.getJSON(address + "/enter", {sid:tokencode[0], token:tokencode[1]}, function(data) {
        if(data["status"] == "ok") {
            user=data["uid"];
            session=data["sid"];
            console.log("/enter got user " + user + " with session " + session);
            pull();
            interval = window.setInterval(push, 1000);
        } else {
            console.log("/enter got fail");
        }
    });
}

function pull() {
    $.getJSON(address + "/pull", {uid: user, sid:session}, function(data) {
        if(data["status"] == "ok") {
            revision = data["revision"];
            $("#thetext").val(data["data"]);
            cache = data["data"];
        } else {
            console.log("/pull got fail");
        }
    });
}

function endSession() {
    $.getJSON(address + "/end", {uid: user, sid:session}, function(data) {
        if(data["status"] == "ok") {
            console.log("/end'ed session " + session + " successfully")
            clearInterval(interval);
        } else {
            console.log("/end got fail");
        }
    });
}

function push() {
    thedata = $("#thetext").val();
    if(thedata==cache) return pull();
    cache=thedata;
    $.getJSON(address + "/push", {uid: user, sid:session, data: thedata, revision: revision}, function(data) {
        if(data["status"] == "ok") {
            console.log("/push'ed successfully");
            revision=data["revision"];
        } else {
            console.log("/push got fail, pulling");
            pull();
        }
    });
}

function generateToken() {
    $.getJSON(address + "/generate", {uid: user, sid:session}, function(data) {
        if(data["status"] == "ok") {
            prompt("Copy to other device to link", session + ":" + data["token"])
        } else {
            console.log("/generate got fail");
        }
    });
}
