function ShowChat() {
	  var x = document.getElementById("iframe-container");
	  var y = document.getElementById("show-button");
	  var z = document.getElementById("hide-button");
y.style.display = "none"
x.classList.add('show')
z.style.display = "flex";
}
function HideChat() {
  var x = document.getElementById("iframe-container");
  var y = document.getElementById("show-button");
  var z = document.getElementById("hide-button");
  x.classList.remove('show')
  z.style.display = "none";
  y.style.display = "flex";
}
function getChatBOtReady(){
    $.ajax({
        url: 'https://toptecq.com/check_previous_chat',
        dataType: 'json',
        data: {},
        success: function(data){
            if(data['status'] == true){
                $(".chat-container-iframe").attr("src", data['room_url'])
                $("#show-button").css("display", "none")
                $(".iframe-container").addClass("show")
                $("#hide-button").css("display", "flex")
            }
        }
    })
}