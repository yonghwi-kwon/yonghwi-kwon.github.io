function myFunction(){var e=document.getElementById("dots"),a=document.getElementById("more"),n=document.getElementById("myBtn");"none"===e.style.display?(e.style.display="inline",n.innerHTML="<i class='fa fa-caret-square-down'></i> Read more",a.style.display="none"):(e.style.display="none",n.innerHTML="<i class='fa fa-caret-square-up'></i> Read less",a.style.display="inline")}function decorate_authors(){const e=["Yonghwi Kwon","Jiacheng Li","Erin Avllazagaj","Chijung Jung","JiHo Lee","Bora Lee","Abbas Naderi-Afooshteh","Ali Ahad"];document.querySelectorAll(".paper-author").forEach(a=>{e.forEach(e=>{const n=new RegExp("\\b"+e+"\\b","g");a.innerHTML=a.innerHTML.replace(n,'<u id="author">'+e+"</u>")})})}!function(e){"use strict";function a(){var a=e(window).width(),n=e("#site_header");a<992?(n.addClass("mobile-menu-hide"),setTimeout(function(){n.addClass("animate")},500)):n.removeClass("animate")}function n(){var a=e("#page-ajax-loaded");function n(){a.removeClass("rotateOutDownRight closed"),a.show(),e("body").addClass("ajax-page-visible")}var o=e(".ajax-page-load").each(function(){if(o=e(this).attr("href"),location.hash==location.hash.split("/")[0]+"/"+o.substr(0,o.length-5)){var t=e(this).attr("href");return n(),a.load(t),!1}});e(document).on("click",".site-main-menu, #ajax-page-close-button",function(n){n.preventDefault(),e("#page-ajax-loaded").addClass("rotateOutDownRight closed"),e("body").removeClass("ajax-page-visible"),setTimeout(function(){e("#page-ajax-loaded.closed").html(""),a.hide()},500),location.hash=location.hash.split("/")[0]}).on("click",".ajax-page-load",function(){var a=location.hash.split("/")[0]+"/"+e(this).attr("href").substr(0,e(this).attr("href").length-5);return location.hash=a,n(),!1})}function o(){e(window).scrollTop()>150?e(".lmpixels-scroll-to-top").removeClass("hidden"):e(".lmpixels-scroll-to-top").addClass("hidden")}e(window).on("load",function(){e(".preloader").fadeOut(800,"linear")}).on("resize",function(){a()}).scroll(function(){o()}),e(document).on("ready",function(){var t=0;992>e(window).width()&&(t=25),e(".pt-trigger").mPageScroll2id({layout:"vertical",highlightClass:"active",keepHighlightUntilNext:!1,scrollSpeed:880,scrollEasing:"easeInOutExpo",scrollingEasing:"easeInOutCirc",clickedClass:"",appendHash:!0,offset:t,forceSingleHighlight:!0}),e(".menu-toggle").on("click",function(){e("#site_header").addClass("animate"),e("#site_header").toggleClass("mobile-menu-hide")}),e(".site-main-menu").on("click","a",function(e){a()}),e(".sidebar-toggle").on("click",function(){e("#blog-sidebar").toggleClass("open")}),e(".lmpixels-scroll-to-top").click(function(){return e("body,html").animate({scrollTop:0},400),!1}),window.onhashchange=function(e){location.hash&&n()},e("body").append('<div id="page-ajax-loaded" class="page-ajax-loaded animated rotateInDownRight"></div>'),n(),o()})}(jQuery);
function decorate_conferences()
{
	const conferenceMap = {
	sp: /\bS(?:&|&amp;)P'\d{2}(?!\s*\(Poster\))/g,
	ccs: /\bCCS'\d{2}(?!\s*\(Poster\))/g,
	ndss: /\bNDSS'\d{2}(?!\s*\(Poster\))/g,
	www: /\bWWW'\d{2}(?!\s*\(Poster\))/g,
	ase: /\bASE'\d{2}(?!\s*\(Poster\))/g,
	asplos: /\bASPLOS'\d{2}(?!\s*\(Poster\))/g,
	usenix: /\bUSENIX'\d{2}(?!\s*\(Poster\))/g,
	imc: /\bIMC'\d{2}(?!\s*\(Poster\))/g,
	icse: /\bICSE'\d{2}(?!\s*\(Poster\))/g,
	fse: /\bFSE'\d{2}(?!\s*\(Poster\))/g,
	oopsla: /\bOOPSLA'\d{2}(?!\s*\(Poster\))/g
	};

	const secondtier = {
	acsac: /\bACSAC'\d{2}(?!\s*\(Poster\))/g,
	asiaccs: /\bASIACCS'\d{2}(?!\s*\(Poster\))/g,
	issta: /\bISSTA'\d{2}(?!\s*\(Poster\))/g,
	atc: /\bATC'\d{2}(?!\s*\(Poster\))/g,
	};

	const paperCollections = {};
	Object.keys(conferenceMap).forEach(key => paperCollections[key] = []);

	document.querySelectorAll('p[id^="p"]').forEach(el => {
		const paperNum = el.id.slice(1);
		el.innerHTML = paperNum + ". " + el.innerHTML;
		
		regex = /\bBibTex\b(?![^<]*>)/g;
		el.innerHTML = el.innerHTML.replace(regex, (match) => {
			return `<a href="bib/bibtex.html#${paperNum}" target="_bibtex">${match}</a>`;
		});
		let html = el.innerHTML;

		
		Object.entries(conferenceMap).forEach(([key, regex]) => {
			html = html.replace(regex, (match) => {
				paperCollections[key].push("<a href=\"#${el.id}\">" + paperNum + "</a>");
				return "<u id='toptier'>" + match + "</u>";
			});
		});
		if (html !== el.innerHTML) {
			el.innerHTML = html;
		} else {
			Object.entries(secondtier).forEach(([key, regex]) => {
				html = html.replace(regex, (match) => {
					return "<u id='sectier'>" + match + "</u>";
				});
			});
			el.innerHTML = html;
		}
	});

	Object.keys(paperCollections).forEach(key => {
		const targetElement = document.getElementById(`${key}_papers`);
		
		if(targetElement){
			targetElement.innerHTML = paperCollections[key].join(", ");
		}
		console.log(key + "_papers: ", paperCollections[key].join(", "));
	});
}