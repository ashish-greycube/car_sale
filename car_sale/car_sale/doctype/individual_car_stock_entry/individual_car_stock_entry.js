// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt
var sourceImage ;
var targetRoot;
var maState;

frappe.ui.form.on('Individual Car Stock Entry', {
	onload_post_render: function(frm) {
		$(frm.fields_dict['car_structure_html'].wrapper)
		.html('<div  style="position: relative; display: flex;flex-direction: column;align-items: center;justify-content: center;padding-top: 50px;"> \
		<img  id="sourceImage"   src="/assets/car_sale/image/car_structure.png" style="max-width: 900px; max-height: 80%;"  crossorigin="anonymous" /> \
		<img  id="sampleImage"   src="/assets/car_sale/image/car_structure.png"  style="max-width: 900px; max-height: 100%; position: absolute;" crossorigin="anonymous" /> \
		</div>');
	
		setSourceImage(document.getElementById("sourceImage"));
	
		const sampleImage = document.getElementById("sampleImage");
		sampleImage.addEventListener("click", () => {
		  showMarkerArea(sampleImage);
		});      
	},	
	refresh: function (frm) {
		if (frm.doc.docstatus == 1 && frm.doc.status == "Car Sold Out") {
			if (frm.doc.payment_status == 'Paid') {

				frappe.db.get_list('Journal Entry', {
					fields: ['name'],
					filters: {
						individual_car_entry_reference: frm.doc.name,
						individual_car_entry_type: 'Payment'
					}
				}).then(records => {
					if (records.length == 0) {
						frm.add_custom_button(__('Payment Journal Entry'), function () {
							frappe.call({
								method: "create_payment_journal_entry",
								doc: frm.doc,
								callback: function (r) {
									if (!r.exc) {
										frm.refresh();
									}
								}
							});
						}, __('Create'));
					}
				})
			}

			if (frm.doc.payment_status == 'Paid') {

				frappe.db.get_list('Journal Entry', {
					fields: ['name'],
					filters: {
						individual_car_entry_reference: frm.doc.name,
						individual_car_entry_type: 'Other'
					}
				}).then(records => {
					if (records.length == 0) {
						frm.add_custom_button(__('Other Journal Entry'), function () {
							frappe.call({
								method: "create_other_journal_entry",
								doc: frm.doc,
								callback: function (r) {
									if (!r.exc) {
										frm.refresh();
									}
								}
							});
						}, __('Create'));
					}
				})

			}

			frappe.db.get_list('Sales Invoice', {
				fields: ['name'],
				filters: {
					individual_car_entry_reference: frm.doc.name
				}
			}).then(records => {
				if (records.length == 0) {
					frm.add_custom_button(__('Sales Invoice'), function () {
						frappe.call({
							method: "create_sales_invoice",
							doc: frm.doc,
							callback: function (r) {
								if (!r.exc) {
									frm.refresh();
								}
							}
						});
					}, __('Create'));
				}
			})

		}
	},
	payment_status: function (frm) {
		frm.trigger("toggle_reqd_fields")
	},
	status: function (frm) {
		frm.trigger("toggle_reqd_fields")
	},
	reservation_status: function (frm) {
		frm.trigger("toggle_reqd_fields")
	},
	toggle_reqd_fields: function (frm) {
		frm.toggle_reqd(["mode_of_payment"], frm.doc.payment_status == 'Paid' ? 1 : 0);
		frm.toggle_reqd(["sale_rate"], frm.doc.status == "Car Sold Out" ? 1 : 0);
		if (frm.doc.status == "Car Received") {
			frm.set_df_property('selling_or_return_date', 'reqd', 0)
			frm.set_df_property('customer_buyer', 'reqd', 0)
		} else if (frm.doc.status == "Car Returned") {
			frm.set_df_property('selling_or_return_date', 'reqd', 1)
			frm.set_df_property('customer_buyer', 'reqd', 0)
		} else if (frm.doc.status == "Car Sold Out") {
			frm.set_df_property('selling_or_return_date', 'reqd', 1)
			frm.set_df_property('customer_buyer', 'reqd', 1)
		}
	},
	validate: function(frm){
		if (frm.doc.status == "Car Sold Out" && frm.doc.sale_rate<=0) {
			frappe.throw(__('As car is Sold Out, please put correct sale rate value.'));
		}		
	}
});

function setSourceImage(source) {
	sourceImage = source;
	targetRoot = source.parentElement;
  }
  
  function showMarkerArea(target) {
	const markerArea = new markerjs2.MarkerArea(sourceImage);
	  markerArea.renderImageQuality = 0.5;
	  markerArea.renderImageType = 'image/jpeg';
  
	// since the container div is set to position: relative it is now our positioning root
	// end we have to let marker.js know that
	markerArea.targetRoot = targetRoot;
	markerArea.addRenderEventListener((imgURL, state) => {
	  target.src = imgURL;
	  // save the state of MarkerArea
	  cur_frm.doc.car_structure_annotation=JSON.stringify(state)
	 
	  cur_frm.set_value('annotated_car_image_cf', imgURL)
	  cur_frm.save()
	});
	markerArea.show();
	// if previous state is present - restore it
	if (cur_frm.doc.car_structure_annotation) {
	  markerArea.restoreState(JSON.parse(cur_frm.doc.car_structure_annotation));
	}
  }