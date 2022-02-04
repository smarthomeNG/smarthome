/*
 * This file contains a binding function with some useful datatables options
 * It can be implemented in the web interface page of a plugin by using
 * <script>
 *     $(document).ready( function () {
 *		     $(window).trigger('datatables_defaults');
 *     });
 * </script>
 */
$(window).bind('datatables_defaults', function() {
	// jQuery fix possible performance issue on scrolling
	// https://stackoverflow.com/questions/39152877/
	jQuery.event.special.touchstart = {
		setup: function( _, ns, handle ) {
				this.addEventListener("touchstart", handle, { passive: !ns.includes("noPreventDefault") });
		}
	};
	jQuery.event.special.touchmove = {
    setup: function( _, ns, handle ) {
        this.addEventListener('touchmove', handle, { passive: !ns.includes('noPreventDefault') });
    }
	};
	try
		{
			// Set datatable useful defaults
			$.extend( $.fn.dataTable.defaults, {
				lengthMenu: [ [25, 50, 100, -1], [25, 50, 100, "All"] ], // pagination menu
				pageLength: 100, // default to "all"
				pagingType: "full_numbers", // include first and last in pagination menu
				colReorder: true, // enable colomn reorder by drag and drop
				fixedHeader: {header: true, // header will always be visible on top of page when scrolling
				 						 headerOffset: $('#webif-navbar').outerHeight() + $('#webif-tabs').outerHeight()},
				responsive: true, // enable responsive extension.
				autoWidth: false,
				"fnDrawCallback": function(oSettings) { // hide pagination if not needed
					if (oSettings._iDisplayLength > oSettings.fnRecordsDisplay() || oSettings._iDisplayLength == -1) {
						 $(oSettings.nTableWrapper).find('.dataTables_paginate').hide();
					} else {
							$(oSettings.nTableWrapper).find('.dataTables_paginate').show();
					}
					$.fn.dataTable.tables({ visible: true, api: true }).fixedHeader.adjust();
				}
			});
			// Set date format for correct sorting of columns containing date strings
			$.fn.dataTable.moment('DD.MM.YYYY HH:mm:ss');
			$('a[data-toggle="tab"]').on('shown.bs.tab', function(e){
				$.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
				$.fn.dataTable.tables({ visible: true, api: true }).fixedHeader.adjust();
				$.fn.dataTable.tables({ visible: true, api: true }).responsive.recalc();
			});
		}
	catch (e)
		{
		console.log("Datatable JS not loaded, showing standard table without reorder option" + e)
		}
});
