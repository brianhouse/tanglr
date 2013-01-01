var background = chrome.extension.getBackgroundPage();  

function updateButton () {
    background.console.log("popup.updateButton " + background.active);
    if (background.active) {
        $('#on_btn').hide();
        $('#off_btn').show();
    } else {
        $('#on_btn').show();
        $('#off_btn').hide();
    }
}
        
function turnOn () {
    background.console.log("popup.turnOn");
    background.turnOn();
    updateButton();     
    background.status = "Waiting for a partner...";
    $('#status').html(background.status);             
    // setTimeout(window.close, 2000);
}

function turnOff () {   
    background.console.log("popup.turnOff");    
    background.turnOff();
    updateButton();
    background.status = "Not entangled.";
    $('#status').html(background.status);             
    // setTimeout(window.close, 2000);
}        

function cancel () {
    background.console.log("popup.cancel");    
    window.close();
}

$(document).ready(function() {
    updateButton();
    $('#on_btn').click(turnOn);
    $('#off_btn').click(turnOff);
    $('#cancel_btn').click(cancel);
    $('#status').html(background.status);
});        