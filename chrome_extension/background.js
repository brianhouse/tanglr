var SERVER = "localhost:5000";
var status = "Not entangled.";
var ws = null;
var active = false;
var current_url = "NONE";
var user_id = null;
var updateButton = null;

function turnOn () {
    console.log("background.turnOn");  
    ws = new WebSocket("ws://" + SERVER + "/websocket");
    active = true;
    ws.onmessage = function (evt) {
        message = evt.data;
        console.log("--> received " + message);
        if (message.substr(0, 4) == "http") {
            var url = evt.data;    
            chrome.tabs.getSelected(null, function (tab) {
                if (tab != null) {
                    console.log(current_url + " vs " + url);
                    if (current_url != url) {
                        chrome.tabs.update(tab.id, {url: url});
                        current_url = url;
                    }
                }
            });  
        } else if (message == "entangled") {                                   
            console.log("entangled");
            status = "Entangled!";
            updateButton();
        } else if (message == "unentangled") {                                   
            console.log("unentangled");
            status = "Waiting for partner...";
            updateButton();            
        } else if (message != "OK") {
            user_id = message;
            console.log("user_id is " + user_id);
            checkUrl();
        }
    };
}

function turnOff () {
    console.log("background.turnOff");  
    ws.close();
    ws.onmessage = null;
    ws = null;
    active = false;
    current_url = "NONE";
    user_id = null;    
}

function checkUrl () {
    if (!active) return;
    console.log("background.checkUrl");  
    chrome.windows.getCurrent(function (window) {
        if (window == null || !window.focused) {
            console.log('(using other application)');
        } else {
            chrome.tabs.getSelected(null, function (tab) {
                if (tab != null) {
                    if (tab.url != current_url) {
                        if (tab.url.substr(0, 4) != "http") {
                            console.log("(settings page)");                            
                        } else {
                            current_url = tab.url;
                            postUrl();
                        }
                    } else {
                        console.log("(same url)");
                    }
                } else {
                    console.log("(no tabs)");
                }
            });                        
        }
    });    
}

function postUrl () {
    console.log("background.postUrl " + current_url);
    if (ws != null) {
        ws.send('{"user_id": "' + user_id + '", "url": "' + current_url + '"}');
    }
}

chrome.tabs.onSelectionChanged.addListener(function (tab_id, select_info) {
    checkUrl();
});

chrome.tabs.onUpdated.addListener(function (tab_id, change_info, tab) {
    checkUrl();
});        

chrome.windows.onFocusChanged.addListener(function (window_id) {
    checkUrl();
});        

chrome.windows.onRemoved.addListener(function (window_id) {
    checkUrl();
});        