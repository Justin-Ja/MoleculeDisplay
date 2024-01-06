$(document).ready(
  /* this defines a function that gets called after the document is in memory */
  function()
  {

    fetch("/fetchData")
      .then(response => response.text())
      .then(body => {
        let data = JSON.stringify(body);
        data = JSON.parse(data);
        temp = data.split("\n");
        jsonInfo = temp[temp.length-1];
        jsonInfo = jsonInfo.split("[");
        jsonInfo = jsonInfo[1].split(",");

        //This removes brackets left on the last number
        jsonInfo[jsonInfo.length -1] = jsonInfo[jsonInfo.length -1].substr(0,3);

        for(let i = 0; i < jsonInfo.length; i = i + 3){
          jsonInfo[i] = jsonInfo[i].trim();
          jsonInfo[i + 1] = jsonInfo[i + 1].trim();
          jsonInfo[i + 2] = jsonInfo[i + 2].trim();
          jsonInfo[i] = jsonInfo[i].substr(1, jsonInfo[i].length - 2)
        }
        console.log(jsonInfo);

        const numButtons = (jsonInfo.length / 3);
        const radioButtonsContainer = document.getElementById('radial_buttons');
        let j = 0;
        // Create and append the radio buttons to the container
        for (let i = 1; i <= numButtons; i++) {
          const radioButton = document.createElement('input');
          radioButton.type = 'radio';
          radioButton.name = 'radio-group';
          radioButton.value = `${jsonInfo[j]}`;
          radioButtonsContainer.appendChild(radioButton);

          const label = document.createElement('label');
          label.for = `${jsonInfo[j]}`;
          label.textContent = `${jsonInfo[j]}, Number of atoms: ${jsonInfo[j+1]}, Number of bonds: ${jsonInfo[j+2]}`;
          radioButtonsContainer.appendChild(label);
          radioButtonsContainer.appendChild(document.createElement("BR"));
          radioButtonsContainer.appendChild(document.createElement("BR"));
          j = j + 3;
       }

   })

       /* add a click handler for our button */
    $("#home_form_button").click(
          function()
          {
    	/* ajax post */
    	$.post("/display_handler",
    	  /* pass a JavaScript dictionary */
    	  {
    	    name: $('input[name="radio-group"]:checked').next('label').text(),
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
