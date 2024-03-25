var say = (message) => {
  $("#chat-wrapper").prepend(
    $(".chat-left.message")
    .last()
    .clone()
    .html(message.replace(/\n/g, '<br>'))
  )
}

$("document").on("ready",()=>{
  say("Hello, how can I help you ?")
  $(".chat-left.message").toggle()
})

function handleKeyDown( event ){
  if ( ((event.keyCode === 13) || (event.type == "click") ) && /\S/.test($("#interface").val())){
    event.preventDefault();

    if(event.shiftKey){
      // Insert a newline character at the current cursor position
      const textarea = $("#interface")[0]
      const cursorPos = textarea.selectionStart;
      const textBeforeCursor = textarea.value.substring(0, cursorPos);
      const textAfterCursor = textarea.value.substring(cursorPos);
      textarea.value = textBeforeCursor + "\n" + textAfterCursor;

      // Move the cursor to the new position
      textarea.setSelectionRange(cursorPos + 1, cursorPos + 1);
    }else{

      $("#chat-wrapper").prepend(
        $(".chat-right")
        .last()
        .clone()
        .removeClass("d-none")
        .text(
            $("#interface").val()
          )
      )
      $("#interface").selectionStart = 0;
      $("#interface").selectionEnd = 0;
        

          

      //Send question
      

      var form = new FormData();
      form.append("prompt",$("#interface").val());
      $("#interface").val(" ");
      $.ajax({
        type: 'POST',
        url: 'https://rdi.behit.net/content_creator/get_response',
        "processData": false,
        "mimeType": "multipart/form-data",
        "contentType": false,
        "data": form,
        success: function(response){
          // Handle success response

          res = $.parseJSON(response)
          console.log($.parseJSON(response));  
          say(`
            ${res["1-Chat response"]} 
            <span class='badge bg-success'>Current_prompt_tokens : ${res["2-Current_prompt_tokens"]}</span>
            <span class='badge bg-success'>Current_completion tokens : ${res["3-Current_completion tokens"]}</span>
            <span class='badge bg-success'>Total_prompts_cost : ${res["4-All_prompts_cost"]}</span>
            <span class='badge bg-success'>Total_responses_cost : ${res["5-All_responses_cost"]}</span>
            <span class='badge bg-success'>All_conversation_cost : ${res["6-Full_conversation_cost"]}</span>
          `)
          
        },
        error: function(xhr, status, error){
          // Handle error response
          console.error(error);
          say("Sorry there is an error please try again !")
        }
      });
      


    }

  }
}


$("#send").on("click",handleKeyDown)



// Show our Chat Interface:
$("#chat-container").slideToggle();


// Listen on the user's input:
$("#interface").on("keydown", handleKeyDown );

$("#riva-btn").on("click",(event)=>{
  handleKeyDown(event)

})