// requirejs.config({
//   paths: {
//     "eventie": "components/eventie/eventie",
//     "eventEmitter": "components/eventEmitter/EventEmitter"
//   }
// });
jQuery.fn.delay = function(time,func){
    this.each(function(){
    	setTimeout(func,time);
    });

    return this;
};

$(document).ready(function(){
	$('body').on('click','.oe_kanban_show_more button', function() {
	images_interval = setInterval(function(){openerp.load_images()},1000);
	});

	$('body').on('click','.oe_pager_group', function(){
		image_interval = setInterval(function(){openerp.load_image()},1000);
	});

	$('body').on('click','.oe_button.oe_form_button_create', function(){
		image_interval = setInterval(function(){openerp.load_image()},1000);
	});

	$('body').on('click','.oe_kanban_image', function(){
		image_interval = setInterval(function(){openerp.load_image()},1000);
	});

	$('body').on('click','.oe_kanban_action.oe_kanban_action_a', function(){
		image_interval = setInterval(function(){openerp.load_image()},1000);
	});
});

openerp.load_image = function(){
		image_url = $('#web_image').text().trim()
		$('img[name="image_medium"]').attr("src", image_url);
		if($('img:not([src])').size() == 0) {
			if (typeof image_interval != 'undefined')
				clearInterval(image_interval);
			image_interval = undefined
		}
	}

openerp.load_images = function() {
	$.each($('.web_images'), function(k,v) {
		image_url = $(v).text().trim();
		$(v).next().attr("src", image_url);
	});
	if($('img:not([src])').size() == 0) {
		if (typeof images_interval != 'undefined')
			clearInterval(images_interval);
		images_interval = undefined
	}
}

