
$(document).ready(
  /* this defines a function that gets called after the document is in memory */
  function()
  {

    $('input[type=radio][name=AR-Group]').change(function() {
      if (this.value == 'Add') {
          $(".add").removeAttr('disabled')
      }
      else if (this.value == 'Remove') {
          $(".add").attr('disabled', 'disabled')
      }
    });
    /* add a click handler for our button */
    $("#update_submit").click(
      function()
      {
	/* ajax post */
  	const form = $("element_form");
  	const formData = new FormData(form);

	$.post("/updateElements_handler",formData,
	  function( data, status )
	  {
	    alert( "Data: " + data + "\nStatus: " + status );
	  }
	);
      }
    );
  }
);
