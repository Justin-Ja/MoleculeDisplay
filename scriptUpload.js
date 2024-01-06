
$(document).ready(
  /* this defines a function that gets called after the document is in memory */
  function()
  {

    /* add a click handler for our button */
    $("#upload_button").click(
      function()
      {
	/* ajax post */
	$.post("/upload_handler.html",
	  /* pass a JavaScript dictionary */
	  {
	    name: $("#sdf_name").val(),	/* retreive value of name field */
	    file: $("#sdf_file").val()
	  },
	  function( data, status )
	  {
	    alert( "Data: " + data + "\nStatus: " + status );
	  }
	);
      }
    );
  }
);
