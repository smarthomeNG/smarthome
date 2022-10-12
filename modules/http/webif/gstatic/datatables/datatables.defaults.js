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
			top_offset = $('#webif-navbar').outerHeight() + $('#webif-tabs').outerHeight();
			// Set datatable useful defaults
			$.extend( $.fn.dataTable.defaults, {
				lengthMenu: [ [25, 50, 100, -1], [25, 50, 100, "All"] ], // pagination menu
				pageResize: false,
				lengthChange: true,
				paging: true,
				pageLength: 100, // default to "100"
				pagingType: "full_numbers", // include first and last in pagination menu
				colReorder: true, // enable colomn reorder by drag and drop
				columnDefs: [{ targets: '_all', className: 'truncate' }],
				fixedHeader: {header: true, // header will always be visible on top of page when scrolling
				 						 headerOffset: top_offset},
				autoWidth: false,
				initComplete: function () {$(this).show();setTimeout(function() { $(window).resize(); }, 300);}, // show table (only) after init, adjust height of wrapper after 300ms (for Safari)
        responsive: {details: {renderer: $.fn.dataTable.Responsive.renderer.listHidden()}}, //makes it possible to update columns even if they are not shown as columns (but as collapsable items)
				preDrawCallback: function (oSettings) {
        	pageScrollPos = $(oSettings.nTableWrapper).find('.dataTables_scrollBody').scrollTop();
					bodyScrollPos = $('html, body').scrollTop();
    		},
				drawCallback: function(oSettings) { // hide pagination if not needed
					if (oSettings._iDisplayLength > oSettings.fnRecordsDisplay() || oSettings._iDisplayLength == -1) {
						 $(oSettings.nTableWrapper).find('.dataTables_paginate').hide();
					} else {
							$(oSettings.nTableWrapper).find('.dataTables_paginate').show();
							$(oSettings.nTableWrapper).find('.paginate_button').on('click', function(){
								// scroll to top on page change
								  $('html, body').animate({
									  scrollTop: $('#'+oSettings.sTableId).offset().top - top_offset
								  }, 'slow');
							});
					}
					$.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
					$.fn.dataTable.tables({ visible: true, api: true }).fixedHeader.enable( false );
					$.fn.dataTable.tables({ visible: true, api: true }).fixedHeader.enable( true );
					$.fn.dataTable.tables({ visible: true, api: true }).fixedHeader.adjust();
					$.fn.dataTable.tables({ visible: true, api: true }).responsive.recalc();
					$('html, body').scrollTop(bodyScrollPos);
					$(this).addClass( "display" );
				},
				createdRow: function (row, data, index) {
					$(row).hide().fadeIn('slow');
					$('td', row).addClass('py-1 truncate');
					$.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
					$.fn.dataTable.tables({ visible: true, api: true }).fixedHeader.adjust();
					$.fn.dataTable.tables({ visible: true, api: true }).responsive.recalc();
				}

			});
			// Set date format for correct sorting of columns containing date strings
			$.fn.dataTable.moment('DD.MM.YYYY HH:mm:ss');
			$.fn.dataTable.moment('YYYY-MM-DD HH:mm:ss');
			$.fn.dataTable.moment('DD.MM.');
			$.fn.dataTable.moment('DD.MM.YY');
			$.fn.dataTable.moment('HH:mm');

			$('a[data-toggle="tab"]').on('shown.bs.tab', function(e){

				$.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
				$.fn.dataTable.tables({ visible: true, api: true }).fixedHeader.adjust();
				$.fn.dataTable.tables({ visible: true, api: true }).responsive.recalc();
				$(function () {
						$(window).resize();
						setTimeout(function() { $(window).resize(); }, 300); // necessary for Safari
				});
			});

		}
	catch (e)
		{
		console.log("Datatable JS not loaded, showing standard table without reorder option" + e)
		}
});
