// Global variables

var phone = document.getElementById("phone")
var video = document.getElementById("video")

// Phone responsive sizing

window.onload = recalculate
window.onresize = recalculate

function recalculate() {
	
	if (window.innerWidth > 414) {
		
		phoneSize = window.innerHeight * 0.016
		if (phoneSize < 14) {
			
			phoneSize = 14
		}
		
		phone.style.fontSize = phoneSize + "px"
	} else {
		
		phone.style.fontSize = null
	}
}

// Video playback

video.onclick = function() {
	video.play()
}

// Video audio controls

var videoIsMuted = true

var audioSwitch = document.getElementById("audio-switch")
var mutedIcon = document.getElementById("muted-icon")
var unmutedIcon = document.getElementById("unmuted-icon")

document.getElementById("audio-button").onclick = function() {
	
	if (videoIsMuted == true) {
		video.muted = false
		videoIsMuted = false
		
		audioSwitch.style.backgroundColor = "#C4C4C4"
		audioSwitch.style.height = "2.9em"
		audioSwitch.style.width = ".3em"
		mutedIcon.style.opacity = 0
		unmutedIcon.style.opacity = 1
				
	} else {
		
		video.muted = true
		videoIsMuted = true
		
		audioSwitch.style.backgroundColor = null
		audioSwitch.style.height = null
		audioSwitch.style.width = null
		mutedIcon.style.opacity = 1
		unmutedIcon.style.opacity = 0
	}
}

// Confetti

var confettis = [document.getElementById("circle-confetti"),
				 document.getElementById("line-confetti"),
				 document.getElementById("square-confetti"),
				 document.getElementById("triangle-confetti")]
				 
var confettiColors = ["#765CFF", "#23E9AD", "#1DC9EA", "#FFD14D"]

var animations = ["confetti", "confetti2"]
				 
document.getElementById("logo-conteiner").onclick = function() {
	
	for (i = 0; i < 12; i++) {
		
		index = i % 3
		
		confetti = confettis[index].cloneNode(true)
		
		randomX = Math.random() * (window.innerWidth - 30)
		randomColor = Math.floor(Math.random() * 4);
		randomSpeed = 6 - Math.floor(Math.random() * 3);
		randomAnimation = Math.floor(Math.random() * 2);
		
		confetti.removeAttribute("id")
		confetti.style.left = randomX + "px"
		confetti.style.fill = confettiColors[randomColor].toString()
		confetti.style.animation = animations[randomAnimation] + " " + randomSpeed + "s linear"
		document.body.appendChild(confetti)
	}
}

// Store buttons hover animation

var speaker = document.getElementById("speaker")
var button = document.getElementById("button")

document.getElementById("play-store-button").onmouseover = function() {
	
	phone.style.backgroundColor = "black"
	phone.style.borderRadius = "1.5em"
	
	speaker.style.width = "7em"
	speaker.style.height = ".5em"
	speaker.style.borderRadius = ".25em"
	speaker.style.margin = "1.9em 7.35em 0"
	speaker.style.backgroundColor = "#424242"
	
	button.style.width = "7em"
	button.style.height = "0"
	button.style.margin = "-2.5em 7.35em 0"
	button.style.borderColor = "#424242"
}

document.getElementById("app-store-button").onmouseover = function() {
	
	phone.style.backgroundColor = null
	phone.style.borderRadius = null
	
	speaker.style.width = null
	speaker.style.height = null
	speaker.style.borderRadius = null
	speaker.style.margin = null
	speaker.style.backgroundColor = null
	
	button.style.width = null
	button.style.height = null
	button.style.margin = null
	button.style.borderColor = null
}