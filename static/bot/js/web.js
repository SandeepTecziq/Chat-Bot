function ShowChat() {
	  var x = document.getElementById("iframe-container");
	  var y = document.getElementById("show-button");
	  var z = document.getElementById("hide-button");
		y.style.display = "none"
		x.style.display = "block";
		z.style.display = "block";
//    var id = null;
//	var elem = document.getElementById("chat-container-iframe");
//    var pos = elem.offsetHeight;
//    var pos_new = elem.offsetHeight;
//    clearInterval(id);
//    elem.style.height = pos + 'px';
//    id = setInterval(frame, 2);
//    function frame() {
//    if (pos == 500) {
//            if(pos_new == 0){
//            clearInterval(id);
//            }
//            else{
//            elem.style.height = pos_new + 'px'
//            pos_new--;
//            }
//
//
//    } else {
//          if(pos_new > 500){
//            clearInterval(id);
//            }
//            else{
//            elem.style.height = pos_new + 'px'
//            pos_new++;
//            }
//        }
//    }
}
function HideChat() {
  var x = document.getElementById("iframe-container");
  var y = document.getElementById("show-button");
  var z = document.getElementById("hide-button");
  x.style.display = "none";
  z.style.display = "none";
  y.style.display = "block";
}