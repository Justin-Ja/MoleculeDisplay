let tempNameStorage = "";

$(document).ready(
  /* this defines a function that gets called after the document is in memory */
  function()
  {

    fetch("/getDisplay")
      .then(response => response.text())
      .then(body => {
        body = JSON.stringify(body);
        let data = JSON.parse(body);
        let temp = data.split('{')[1].slice(0,-1);

        temp = temp.split(':');
        svg = temp[1] + temp[2];
        tempNameStorage = temp[3];
        tempNameStorage = tempNameStorage.replaceAll("\"", "");
        tempNameStorage = tempNameStorage.replaceAll(" ", "");

        svg = svg.trim();
        svg = svg.substring(0, svg.length - 8)
        test = JSON.parse(svg)
        let svgDiv = document.querySelector('#svg_div');
        // insert before the closing tag
        svgDiv.insertAdjacentHTML('beforeend', test);
        inputField = document.getElementById("molName")
        inputField.value = tempNameStorage;
   })

       /* add a click handler for our button */
    $("#displayButtonForm").click(
          function()
          {
    	/* ajax post */
    	$.post("/rotate",
    	  /* pass a JavaScript dictionary */
    	  {
          name: $("molName").val(),
    	    xRot: $("Xrot").val(),
          yRot: $("Yrot").val(),
          zRot: $("Zrot").val(),
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
