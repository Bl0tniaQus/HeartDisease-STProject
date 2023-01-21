function clear(divs)
{
	divs.forEach(div => div.style.display = "none");
}
function setClick(options, divs)
{
	options.forEach(option => option.onclick = function(){
		clear(divs)
		let id = this.id.split('_');
		document.querySelector("#contentw_"+id[1]).style.display = "block";
		});
}
var divs = document.querySelectorAll("div[id^=contentw_]");
var options = document.querySelectorAll("li[id^=wynik_]");
clear(divs);
setClick(options,divs);


