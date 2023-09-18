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
				lengthMenu: [ [1, 25, 50, 100, -1], ["Auto", 25, 50, 100, "All"] ], // pagination menu
				lengthChange: true,
				paging: true,
				pageResize: true,
				stateSave: true,
				pageLength: 100, // default to "100"
				pagingType: "full_numbers", // include first and last in pagination menu
				colReorder: true, // enable colomn reorder by drag and drop
				columnDefs: [{className: 'dtr-control datatable-responsive', orderable: false, targets: 0}, { targets: '_all', className: 'truncate' }],
				order: [[1, 'asc']],
				fixedHeader: {header: true, // header will always be visible on top of page when scrolling
				 						 headerOffset: top_offset},
				autoWidth: false,
				initComplete: function (oSettings) {
					// update content on ordering - if activated
					$(this).on( 'click', 'thead tr th', function () {
						if ($(this).hasClass( "sorting" ) && window.initial_update == 'true'){
							console.log("Instant value update after sorting");
							shngGetUpdatedData(null, null, 0);
						}
					});
					// slightly change resize_wrapper when expanding/collapsing responsive rows to fix some issues
					$(this).on( 'click', 'tbody tr td', function () {
						if ($(this).hasClass( "datatable-responsive" )){
							window.toggle = window.toggle * -1 + 0.1;
							console.log("click responsive, recalc");
							// Don't resize as it might mess up pagination when responsive icon is clicked...
							//$(window).resize();
							$(this).parent().parent().parent().DataTable().responsive.recalc();
						}
					});
					// update content on searching - if activated
					$(".dataTables_filter").change( function () {
						if (window.initial_update == 'true'){
							console.log("Instant value update after search filter");
							shngGetUpdatedData(null, null, 0);
						}
					});
					// Warning if first column is not empty (for responsive + sign)
					td_content = $(this).find('tbody').find('td:first-child').html();
					if (td_content != '' && td_content != 'No data available in table')
						console.warn("First column has to be empty! The plugin author has to add an empty first column in thead and tbody of " + $(this).attr('id'));

					this.api().columns.adjust();
					this.api().responsive.recalc();
					initialized = true;
					$(this).show();
					// update pagelength and save cookie
					let tab = $(this).closest('.tab-pane').attr('id');
					window.pageLength[tab]['tableid'] = this.attr('id');
					setCookie("pagelength", window.pageLength, 30, window.pluginname);

					if (typeof window.row_count !== 'undefined' && window.row_count !== 'false') {
						setTimeout(function() { window.row_count = $.fn.dataTable.tables({ visible: true, api: true }).rows( {page:'current'} ).count(); console.log("Row count after init is " + window.row_count);}, 200);
					}
					console.log("Instant value update is " + window.initial_update + ", already run: " + window.initial_update_run);
					if (window.initial_update == 'true' && window.initial_update_run == 0) {
						console.log("Initializing page update on init");
						window.initial_update_run = 1;
						setTimeout(function() { shngGetUpdatedData(null, null, 0); }, 300);
					}
					//setTimeout(function() { $(window).resize();  }, 2000);

				},
        responsive: {details: {type: 'column', renderer: $.fn.dataTable.Responsive.renderer.listHidden()}}, //makes it possible to update columns even if they are not shown as columns (but as collapsable items)
				preDrawCallback: function (oSettings) {

					// scroll
        	pageScrollPos = $(oSettings.nTableWrapper).find('.dataTables_scrollBody').scrollTop();
					bodyScrollPos = $('html, body').scrollTop();

    		},
				drawCallback: function(oSettings) {
					let tab = $(this).closest('.tab-pane').attr('id');
					// Following lines would help to recalculate page raws after changing pages.
					// However it also might mess up pagination! Leave it alone for now...
					//$(window).resize();
					//window.toggle = window.toggle * -1;
					//setTimeout(function() { $(window).resize();  }, 500);


					console.log("draw datatable " + oSettings.sTableId + " in tab " + tab + " with pagelength " + this.api().page.len());
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
									 setTimeout(function() { shngGetUpdatedData(null, null, 0); }, 300);
	 							 }
							});
					}
					$('html, body').scrollTop(bodyScrollPos);
					this.api().fixedHeader.enable( false );
					this.api().fixedHeader.enable( true );
					this.api().fixedHeader.adjust();
					this.api().responsive.recalc();
					$(this).addClass( "display" );
					/*
					if (initialized == true) {
						$(this).find('tbody').find('tr:nth-child(3)').find('td:first-child').click();
					}
					*/
					if (typeof window.row_count !== 'undefined' && window.row_count !== 'false' && initialized == true) {
						setTimeout(function() { window.row_count = $.fn.dataTable.tables({ visible: true, api: true }).rows( {page:'current'} ).count(); console.log("Row count after draw is " + window.row_count);initialized = false;}, 200);
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
						console.log("resize datatable after tab change");
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
