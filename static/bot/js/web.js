function ShowChat() {
	  var x = document.getElementById("iframe-container");
	  var y = document.getElementById("show-button");
	  var z = document.getElementById("hide-button");
y.style.display = "none"
x.classList.add('show')
z.style.display = "block";
}
function HideChat() {
  var x = document.getElementById("iframe-container");
  var y = document.getElementById("show-button");
  var z = document.getElementById("hide-button");
  x.classList.remove('show')
  z.style.display = "none";
  y.style.display = "block";
}