function clear(divs)
{
	divs.forEach(div => div.style.display = "none");
}
function setClick(options, divs)
{
	options.forEach(option => option.onclick = function(){
		clear(divs)
		id = this.id.split('_');
		document.querySelector("#contentw_"+id[1]).style.display = "block";
		});
}
divs = document.querySelectorAll("div[id^=contentw_]");
options = document.querySelectorAll("li[id^=wynik_]");
clear(divs);
setClick(options,divs);


