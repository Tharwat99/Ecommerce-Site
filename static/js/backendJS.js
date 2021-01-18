$(function(){
	'use strict';
	//Hide PlaceHolder On Form Focus And Show on blur
	$('input[placeholder]').focus(function(){		
		$(this).attr("data",$(this).attr('placeholder'));
		$(this).attr('placeholder','');
	}).blur(function(){
		$(this).attr('placeholder',$(this).attr("data"));
	});

	// show and hide password 
	var pass = $(".pass");
	
	$(".pass-eye").hover(function(){
		pass.attr("type","text");
	},function(){
		pass.attr("type","password");
	});
	//$(".header").height($(window).height());
	//The Time of move background on carsouel
	$(".carousel").carousel({
		interval:4000,
	});

	// arrow down and up
	$(".arrow-down").click(function(){
		if($(this).hasClass('down'))
		{
			$("html , body").animate({scrollTop:$(".shop").offset().top},500);
	     	$(this).toggleClass("down");
			$(this).html("<i class = 'fa fa-chevron-up fa-3x'></i>");
	    }
	    else
	    {
	    	$("html , body").animate({scrollTop:$(".carousel").offset().top},500);
			$(this).toggleClass("down");
			$(this).html("<i class = 'fa fa-chevron-down fa-3x'></i>"); 
		}
	});
	$(window).on("scroll",function(){
		var s = $(window).scrollTop();
		if($(window).scrollTop() >= $(window).height())
		{
			$(".arrow-down").html("<i class = 'fa fa-chevron-up fa-3x'></i>");
		}
		else
		{
			$(".arrow-down").html("<i class = 'fa fa-chevron-down fa-3x'></i>");
		}
	});
	
	
});