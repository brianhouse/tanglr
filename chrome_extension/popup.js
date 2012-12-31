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
    window.close();
}

function turnOff () {   
    background.console.log("popup.turnOff");    
    background.turnOff();
    updateButton();
    window.close();
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
});        