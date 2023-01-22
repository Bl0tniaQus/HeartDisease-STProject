document.querySelector("#usunkonto").onclick = function(){

		this.style.display = "none";
		document.querySelector("#usunkonto2").style.display = "block";
		document.querySelector("#potwierdzenie_usuniecia").innerHTML = "Naciśnij przycisk jeszcze raz aby na pewno usunąć konto"
}

