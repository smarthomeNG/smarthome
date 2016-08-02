(function( $, window, document, undefined ) {
	var Reload = function(elem, options) {
		this.$elem = $(elem);
		this.options = options;
	};

	Reload.prototype.defaults = {
		time: 3000,
		autoReload: false,
		//beforeReload: function(){},
		//afterReload: function(){},
		parameterString: '',
		parseData: function(){}
	};

	Reload.prototype.init = function() {
		var self = this;

		// Set the configuration parameters
		self.config = $.extend({},self.defaults,self.options);

		// Set the container for refresh animation
		self.config.refreshContainer = $(self.config.refreshContainer) || self.$elem.find('.refresh-container');

		// Set the container to update the data with
		self.config.dataContainer = $(self.config.dataContainer) || self.$elem.find('.data-container');

		self.$elem.find('.fa-refresh').click(self.reload());
		self.$elem.find('.fa-refresh').off('click');
		self.$elem.find('.fa-refresh').on('click', function() {
            self.reload()
        });

		if(self.config.autoReload) {
			setInterval(self.reload,self.config.time);
			_self.$elem.find('.fa-refresh').addClass('fa-spin');
		}

		return self;
	};

	Reload.prototype.reload = function(){
		var _self = this;
        _self.$elem.find('.fa-refresh').addClass('fa-spin');
		_self.config.refreshContainer.fadeIn('fast');
  		// Send the AJAX request to fetch the data
  		$.getJSON(_self.$elem.data('url')+_self.config.parameterString, function(result) {
		    _self.config.parseData(result);
		    if(_self.config.autoReload) {
		        _self.config.refreshContainer.fadeOut("done", function() {});
		    } else {
                _self.config.refreshContainer.fadeOut("done", function() {_self.$elem.find('.fa-refresh').removeClass('fa-spin');});
		    }
		});
	};

	// Register the plugin to JQuery
	$.fn.reload = function(options) {
		this.each(function() {
			var $this, reload;
			$this = $(this);
			reload = new Reload(this, options);
			return reload.init();

		});
	};

})( window.jQuery, window, document );