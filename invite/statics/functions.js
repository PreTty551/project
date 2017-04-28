// Contact pop-over menu interaction

var contactLink = document.getElementById("contact-link")
var contactList = document.getElementById("contact-list")
var contactListCloser = document.getElementById("contact-list-closer")

contactLink.onclick = function() {
	
	contactList.style.visibility = "visible"
	contactList.style.opacity = "1"
	contactList.style.transform = "translateY(0em)"
	
	contactListCloser.style.display = "block"
	
	contactLink.style.fill = "#FF004D"
}

contactListCloser.onclick = function() {
	
	contactList.style.opacity = null
	contactList.style.transform = null
	contactList.style.visibility = null
	
	contactListCloser.style.display = null
	
	contactLink.style.fill = null
}