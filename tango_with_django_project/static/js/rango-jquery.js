$(document).ready(function(){
    console.log("AAA");
    // Jquery code to be added here
    $("#about-btn").click( function(event) {
        msgstring = $("#msg").html()
        msgstring = msgstring + "WOW!"
        $("#msg").html(msgstring)
    });
});