let notification = null;

//display a "toast" notification
function showNotification(text){
    if(notification)
        return;

    notification = document.createElement("div");
    notification.className = "notification";
    notification.innerText = text;
    document.body.appendChild(notification);

    //dispay animation
    setTimeout(() => {
        notification.classList.add("show");
    }, 100);

    //delete the notification after 3 seconds 
    setTimeout(() => {
        notification.classList.remove("show");

        //delete the element after the hiding animation
        setTimeout(() => {
            document.body.removeChild(notification);
            notification = null;
        }, 300);
    }, 3000);
}

//server request
function ajax(url, method, data, success, failure){
    let xhr = new XMLHttpRequest();
    xhr.open(method, url, true);

    xhr.onreadystatechange = function(){
        //if the server returns code 200
        if(xhr.readyState == 4 && xhr.status == 200){
            if(typeof success === "function")
                success(xhr.responseText);
        }
        //if the request wasn't successful, error 400-500
        else if(xhr.readyState == 4){
            if(typeof failure === "function")
                failure(xhr.responseText);
        }
    }

    //sending parameters to the server
    if(method == "POST"){
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhr.send(data);
    }
    else
        xhr.send();
}

//sending location data
function sendLocation(e){
    if(e.key == "Enter")
        ajax("/", "POST", "locatie=" + encodeURIComponent(e.target.value), null, response => {
            showNotification(response);
        });
}

//sending sync option
function syncWatch(e){
    let target = e.target,
        setElement = document.querySelector(".set");

    //disabling the custom time settings if the sync is on
    if(target.checked){
        setElement.classList.add("disabled");
    }
    else{
        setElement.classList.remove("disabled");
    }

    ajax("/", "POST", "sincronizare=" + target.checked);
}

//sending time data
function sendTime(e){
    let hours = document.querySelector("[name=ceas_ora]"),
        minutes = document.querySelector("[name=ceas_minut]");

    //sending data on Enter key press
    if(e.key == "Enter")
        ajax("/", "POST", "ora=" + encodeURIComponent(hours.value + ";" + minutes.value), null, response => {
            showNotification(response);
        });
}

//running on page load
function load(){
    let location = document.querySelector("[name=ceas_locatie]"),
        sync = document.querySelector("[name=ceas_internet]"),
        hours = document.querySelector("[name=ceas_ora]"),
        minutes = document.querySelector("[name=ceas_minut]");

    //attaching event to the element if it exists
    if(location)
        location.addEventListener("keyup", sendLocation);
    if(sync)
        sync.addEventListener("change", syncWatch);
    if(hours)
        hours.addEventListener("keyup", sendTime);
    if(minutes)
        minutes.addEventListener("keyup", sendTime);
}

//function running on page load
window.addEventListener("load", load);