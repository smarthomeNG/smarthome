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
			initialized = false;
			// Set datatable useful defaults
			$.extend( $.fn.dataTable.ext.classes, { "sTable": "table table-striped table-hover pluginList display dataTable dataTableAdditional" });
			$.extend( $.fn.dataTable.defaults, {
				lengthMenu: [ [25, 50, 100, -1], [25, 50, 100, "All"] ], // pagination menu
				pageResize: false,
				lengthChange: true,
				paging: true,
				pageLength: 100, // default to "100"
				pagingType: "full_numbers", // include first and last in pagination menu
				colReorder: true, // enable colomn reorder by drag and drop
				columnDefs: [{className: 'dtr-control datatable-responsive', orderable: false, targets: 0}, { targets: '_all', className: 'truncate' }],
				order: [[1, 'asc']],
				fixedHeader: {header: true, // header will always be visible on top of page when scrolling
				 						 headerOffset: top_offset},
				autoWidth: false,
				initComplete: function () {
					$(this).on( 'click', 'thead tr th', function () {
						if ($(this).hasClass( "sorting" ) && window.initial_update == 'true'){
							console.log("Instant value update after sorting");
							shngGetUpdatedData();
						}
					});
					$(".dataTables_filter").change( function () {
						if (window.initial_update == 'true'){
							console.log("Instant value update after search filter");
							shngGetUpdatedData();
						}
					});
					td_content = $(this).find('tbody').find('td:first-child').html();
					if (td_content != '' && td_content != 'No data available in table')
						console.warn("First column has to be empty! The plugin author has to add an empty first column in thead and tbody of " + $(this).attr('id'));
					$(this).show();
					this.api().columns.adjust();
					this.api().responsive.recalc();
					initialized = true;
					if (typeof window.row_count !== 'undefined' && window.row_count !== 'false') {
						setTimeout(function() { window.row_count = $.fn.dataTable.tables({ visible: true, api: true }).rows( {page:'current'} ).count(); console.log("Row count after init is " + window.row_count);}, 200);
					}
					console.log("Instant value update is " + window.initial_update);
					if (window.initial_update == 'true') {
						setTimeout(function() { shngGetUpdatedData(); }, 200);
					}
					setTimeout(function() { $(window).resize();  }, 2000);// show table (only) after init, adjust height of wrapper after 2s
				},
        responsive: {details: {type: 'column', renderer: $.fn.dataTable.Responsive.renderer.listHidden()}}, //makes it possible to update columns even if they are not shown as columns (but as collapsable items)
				preDrawCallback: function (oSettings) {

        	pageScrollPos = $(oSettings.nTableWrapper).find('.dataTables_scrollBody').scrollTop();
					bodyScrollPos = $('html, body').scrollTop();

    		},
				drawCallback: function(oSettings) { // hide pagination if not needed
					$(window).resize();

					if (oSettings._iDisplayLength > oSettings.fnRecordsDisplay() || oSettings._iDisplayLength == -1) {
						 $(oSettings.nTableWrapper).find('.dataTables_paginate').hide();
					} else {
							$(oSettings.nTableWrapper).find('.dataTables_paginate').show();
							$(oSettings.nTableWrapper).find('.paginate_button').on('click', function(){
								// scroll to top on page change
							  $('html, body').animate({
								  scrollTop: $('#'+oSettings.sTableId).offset().top - top_offset - $(oSettings.nTableWrapper).find('.dataTables_filter').outerHeight() - 10
							  }, 'slow');
	 							 console.log("Instant value update is " + window.initial_update);
	 							 if (window.initial_update == 'true') {
									 setTimeout(function() { shngGetUpdatedData(); }, 200);
	 							 }
							});
					}
					$('html, body').scrollTop(bodyScrollPos);
					this.api().fixedHeader.enable( false );
					this.api().fixedHeader.enable( true );
					this.api().fixedHeader.adjust();
					this.api().responsive.recalc();
					$(this).addClass( "display" );
					if (typeof window.row_count !== 'undefined' && window.row_count !== 'false' && initialized == true) {
						setTimeout(function() { window.row_count = $.fn.dataTable.tables({ visible: true, api: true }).rows( {page:'current'} ).count(); console.log("Row count after draw is " + window.row_count);}, 200);
					}
				},
				createdRow: function (row, data, index) {
					$(row).hide().fadeIn('slow');
					$('td', row).addClass('py-1 truncate');
					this.api().columns.adjust();
					this.api().fixedHeader.adjust();
					this.api().responsive.recalc();
					if (typeof window.row_count !== 'undefined' && window.row_count !== 'false' && initialized == true) {
						setTimeout(function() { window.row_count = $.fn.dataTable.tables({ visible: true, api: true }).rows( {page:'current'} ).count(); console.log("Row count after row creation is " + window.row_count);}, 200);
					}
				}

			});
			// Set date format for correct sorting of columns containing date strings
			$.fn.dataTable.moment('DD.MM.YYYY HH:mm:ss');
			$.fn.dataTable.moment('YYYY-MM-DD HH:mm:ss');
			$.fn.dataTable.moment('MM/DD/YYYY HH:mm:ss');
			$.fn.dataTable.moment('DD.MM.YYYY HH:mm:ss.SSSS');
			$.fn.dataTable.moment('YYYY-MM-DD HH:mm:ss.SSSS');
			$.fn.dataTable.moment('MM/DD/YYYY HH:mm:ss.SSSS');
			$.fn.dataTable.moment('DD.MM.');
			$.fn.dataTable.moment('DD.MM.YY');
			$.fn.dataTable.moment('DD.MM.YYYY');
			$.fn.dataTable.moment('MM/DD/YYYY');
			$.fn.dataTable.moment('MM/DD/YY');
			$.fn.dataTable.moment('HH:mm');
			$.fn.dataTable.moment('HH:mm:ss');
			$.fn.dataTable.moment('HH:mm:ss.SSSS');
			$.fn.dataTable.moment('HH:mm DD.MM.YYYY');
			$.fn.dataTable.moment('HH:mm:ss DD.MM.YYYY');
			$.fn.dataTable.moment('HH:mm:ss.SSSS DD.MM.YYYY');

			$('a[data-toggle="tab"]').on('shown.bs.tab', function(e){
				window.activeTab = $(this).attr("href").replace("#", "") ;
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
