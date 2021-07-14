function get_notification(note_id) {

    var spanText = document.getElementById(note_id).innerText;
    if (spanText == '') {
        document.getElementById(note_id).innerText = 1
        document.getElementById(note_id).classList.add("notification")
    } else {
        document.getElementById(note_id).innerText = parseInt(spanText) + 1
    }

}

function updateElementIndex(el, prefix, ndx) {
   var id_regex = new RegExp('(' + prefix + '-\\d+-)');
   var replacement = prefix + '-' + ndx + '-';
   if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex,
   replacement));
   if (el.id) el.id = el.id.replace(id_regex, replacement);
   if (el.name) el.name = el.name.replace(id_regex, replacement);
}

function deleteForm(btn, prefix) {
   var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
   if (formCount > 1) {
       // Delete the item/form

       $(btn).parent().parent().remove();
       var forms = $('.item'); // Get all the forms
       var row_del = $(".item:first").clone(false).get(0);
       // Update the total number of forms (1 less than before)
       $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
       var i = 0;
       // Go through the forms and set their indices, names and IDs
       for (formCount = forms.length; i < formCount; i++) {
           $(forms.get(i)).children().children().each(function () {
              // if ($(this).attr('type') == 'text')
                updateElementIndex(this, prefix, i);
           });
       }
   } // End if
   else {
       alert("You have to enter at least one todo item!");
   }
   return false;
}

function addForm(btn, prefix) {
   var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
   // You can only submit a maximum of 10 todo items
   if (formCount < 1000) {
       // Clone a form (without event handlers) from the first form
       var row = $(".item:first").clone(true).get(0);
       // Insert it after the last form
       $(row).removeAttr('id').hide().insertAfter(".item:last").slideDown(300);

       // Remove the bits we don't want in the new row/form
       // e.g. error messages
       $(".errorlist", row).remove();
       $(row).children().removeClass("error");

       // Relabel or rename all the relevant bits

       $(row).children().children().each(function () {
           updateElementIndex(this, prefix, formCount);
           $(this).attr("value","")
           $(this).val('')
       });

       // Add an event handler for the delete item/form link
//               $(row).find(".delete").click(function () {
//                   return deleteForm(this, prefix);
//               });
       // Update the total form count
       $("#id_" + prefix + "-TOTAL_FORMS").val(formCount + 1);
   } // End if
   else {
       alert("Sorry, you can only enter a maximum of ten items.");
   }
   return false;
}

function saveChat(secret_key, uu_id){

  var sent = {}
  var replies = {}
  var chat = {}

  counter = 0
  $("ul li.replies").each(function(){
  replies[counter]  = $(this).text()
  counter++
  })

  counter1 = 0
  $("ul li.sent").each(function(){
  sent[counter1]  = $(this).text()
  counter1++
  })
  $.each(replies, function(key, value){
  chat[value] = sent[key]
  })
  console.log(chat)
  $.ajax({
  url: '{% url "save_chat_customer" %}',
  dataType: 'json',
  data: { 'message': JSON.stringify(chat), 'secret_key': secret_key, 'cust_id':uu_id },
  success: function(data){
  		alert("conversation has been saved.")
    }

  });

}

function selectNumberOfOption($this){
if($this.val() == 'normal'){
    $this.siblings(".number-of-option").hide();
    }
    else if($this.val() == 'option'){
    $this.siblings(".number-of-option").show();
    }
}

function addChatMapQuestion(ques_type, new_serial){
    if($("#add-question").hasClass("not-saved")){
        $(".error-un-saved").removeClass("hidden-element")
        return false;
    }
    var number_question = $(".number-of-option").val()
    if(number_question < 2 | number_question > 10){
        $(".error-option-number").removeClass("hidden-element")
        $(".number-of-option").css("border", "1px solid red")
        return false;
    }
    else{
        $(".number-of-option").css("border", "1px solid #c2c2c2")
        if($(".error-option-number").hasClass("hidden-element")){

        }
        else{
        $(".error-option-number").addClass("hidden-element")
        }
    }
    if(ques_type == 'normal'){
        var cloned = $(".question-type-div .normal-ques").clone(true)
        cloned.find(".serial-number").val(new_serial + 1)
        if(new_serial > 0){
            for(i=0;i<new_serial;i++){
                j = i+1
                if(j == new_serial){
                    cloned.find(".parent-select").append("<option value="+j+" selected>"+j+"</option>")
                }
                else{
                    cloned.find(".parent-select").append("<option value="+j+">"+j+"</option>")
                }
            }
        }
        else{
            cloned.find(".parent-select").hide();
        }
        $(".question-div").append(cloned)
    }
    else if(ques_type == 'option'){
        var number_of_option = $(".number-of-option").val();
        var cloned = $(".question-type-div .option-ques").clone(true)
        cloned.find(".serial-number").val(new_serial + 1)
        if(new_serial > 0){
            for(i=0;i<new_serial;i++){
                j = i+1
                if(j == new_serial){
                    cloned.find(".parent-select").append("<option value="+j+" selected>"+j+"</option>")
                }
                else{
                    cloned.find(".parent-select").append("<option value="+j+">"+j+"</option>")
                }
            }
        }
        else{
            cloned.find(".parent-select").hide();
        }
        for(i=0;i<number_of_option;i++){
            j=i+2+new_serial
            cloned.find(".option-text").append('<p><input type="text" name="option-number" disabled class="serial-number" value='+j+'><input name="option-text" type="text" class="question-option"></p>')
        }
        $(".question-div").append(cloned)
    }
    $("#add-question").addClass("not-saved")
}

function add_scroll_bar(){
    $(".messages").animate({
        scrollTop: $(document).height()
    }, "fast");
    $(".messages").getNiceScroll().resize();
}

function check_blank_question($this, question){
    if(question == ""){
            $this.find(".form-text-single").css("border", "1px solid red")
            $this.find(".error-question-text").removeClass("hidden-element").text("Question field is required.")
            return false;
            }
    else{
        $this.find(".form-text-single").css("border", "1px solid #c2c2c2")
        if($this.find(".error-question-text").hasClass("hidden-element")){

        }
        else{
        $(".error-question-text").addClass("hidden-element")
        }
    }
}

function check_blank_option($this, type){
    if(type == 'option'){
        var checked = 0
         $this.find(".option-text").find("p input.question-option").each(function(){
             if($(this).val() == ""){
                checked = 1
                if($(this).parent().hasClass("error-found")){
                }
                else{
                 $(this).parent().append("<span class='error-list' style='margin-left: 10px;'>This is required.</span>").addClass("error-found")
                 $(this).css("border", "1px solid red")
                }
             }
             else{
                if($(this).parent().hasClass("error-found")){
                    $(this).parent().removeClass("error-found")
                    $(this).parent().find(".error-list").remove()
                    $(this).css("border", "1px solid #c2c2c2")
                }
             }
         });
         if(checked == 1){
         return false;
         }
    }
}

function add_drop_down(){
    var new_serial = $(".question-div .serial-number").length
    var count = 0
    $(".parent-selector").each(function(){
        if(count != 0){
            var parent = $(this).attr("data-parent")
            for(i=0;i<=new_serial;i++){
                if(i==parent){
                    $(this).append("<option value="+i+" selected>"+i+"</option>")
                }
                else{
                    $(this).append("<option value="+i+">"+i+"</option>")
                }
            }
        }
        else{
            $(this).remove()
        }
        count++
    })
}

function select_all($this){
    if($this.prop("checked")){
        $(".single-select").prop("checked", true)
    }
    else{
        $(".single-select").prop("checked", false)
    }
}

function select_all_submit(e){
    e.preventDefault();
    var len = $(".single-select:checked")
    if(len.length == 0){
        $(".if-checked").removeClass("hidden-element")
        $("#selected-items-input").val("")
    }
    else{
        if($(".if-checked").hasClass("hidden-element")){

        }
        else{
            $(".if-checked").addClass("hidden-element")
        }
        var arr = []
        $(".single-select:checked").each(function(){
            arr.push($(this).val())
        })
        $("#selected-items-input").val(arr)
        $("#selectAllModal").modal("show");
    }
}

function add_number(){
    var counter = 1
    $(".question-collection form .form-number").each(function(){
    $(this).val(counter)
    counter++
    })
}

function add_question($this, new_serial){
    if(!$this.hasClass("title-saved-ok")){
        $(".title-div .error-chat-name").removeClass('hidden-element')
        $(".title-div .error-chat-name").html("Please save the Chat Title first.")
        $(".title-div .question-text").css("border", "1px solid red")
        return false;
    }
    var saved = $(".question-collection form:last").attr("data-saved")
    if(saved == "not-saved"){
        alert("There is a un-saved question. Please save or remove before adding new question")
        return true
    }
    var form_type = $this.attr("data-form")
    var carousel_type = $this.attr("data-carousel-type")
    var is_option = $this.attr("data-option")
    var form = $(".form-collection ."+form_type).clone(true)
    if(carousel_type == 'carousel'){
    var num = $this.find('.item').length
    $this.find('total-item-number').val(num)
    }
    form.removeClass("hidden-element")
    form.find(".form-carousel-type").val(carousel_type)
    form.find(".form-is-option").val(is_option)
    form.find(".form_type").val(form_type)
    $(".question-collection").append(form)
    if(new_serial > 0){
            for(i=0;i<new_serial;i++){
                j = i+1
                if(j == new_serial){
                    form.find(".parent-select").append("<option value="+j+" selected>"+j+"</option>")

                    var u_id = $(".parent-"+j).val()
                    form.find('.form-u-id').val(u_id)
                }
                else{
                    form.find(".parent-select").append("<option value="+j+">"+j+"</option>")
                }
            }
        }
    else{
        form.find(".parent-select").hide();
    }
    add_number()
    $this.siblings(".question-type-list").removeClass("active")
    $this.addClass("active")
}

function AddOption($this){
    var cloned = $this.parent().parent().find(".item:first").clone(true)
    cloned.find("input:not('.remove-question-option')").val("")
    cloned.find("textarea").val("")
    cloned.find(".uploaded-image-link").remove()
    cloned.find(".image-count-input").remove()
    cloned.find("span.file-selected").html("")
    var frame_num = parseInt($this.parent().parent().siblings(".hidden-input").find(".total-item-number").val()) + 1
    $this.parent().parent().siblings(".hidden-input").find(".total-item-number").attr("value",frame_num)
    $this.parent().parent(".tertiary-fields").find(".item:last").after(cloned)
    add_number()
    return false;
}

function RemoveOption($this){
    var tot = $this.parent().siblings(".item").length
    if(tot < 2){
    alert("Atleast 2 options required")
    return false
    }
    var frame_num = parseInt($this.parent().parent().siblings(".hidden-input").find(".total-item-number").val()) - 1
    $this.parent().parent().siblings(".hidden-input").find(".total-item-number").attr("value",frame_num)
    $this.parent().remove();

    add_number()
    return false
}

function SelectParent($this){
    var parent = $this.val()
    var u_id = $(".parent-"+parent).val()
    $this.parent().siblings(".hidden-input").find(".u-id-p").find(".form-u-id").val(u_id)
}

function AddParentInSavedQuestion(){
    var new_serial = $(".question-collection .form-number").length
    $(".question-collection .create-question-form").each(function(){
    var parent = $(this).find(".parent-select").attr("data-parent")
    if(parent != ""){
            for(i=1;i<new_serial;i++){

                if(i == parent){
                    $(this).find(".parent-select").append("<option value="+i+" selected>"+i+"</option>")
                }
                else{
                    $(this).find(".parent-select").append("<option value="+i+">"+i+"</option>")
                }
            }
        }
    else{
        $(this).find(".parent-select").hide();
    }
    })
}

function ClickOnSlot($this){
    $(".sent-span").remove();
    var slot_id = $this.attr("id")
    $("#chatID").append("<li class='sent selected-slot msg-li' id='"+slot_id+"'>"+$this.html()+"</li>")
    AppendMessageBox();
    var selected_date = $("#selected-date").text()
    var selected_provider = $(".service-provider-name").text()
    var selected_slot = $(".selected-slot").text()
    $("#booking-date-span").text(selected_date)
    $("#booking-slot-span").text(selected_slot)
    $("#provider-name-span").text(selected_provider)
    setTimeout(function(){
    $("#book-appointment-div").show();
    AppendMessageBox();
    },1500)
}

function setTitleToNewQuestions(pk){
    $(".form-chat-title").attr("value", pk)
}

function AppendMessageBox(){
      $(".messages").stop().animate({ scrollTop: $(".messages")[0].scrollHeight}, 1000);
//    $(".messages").getNiceScroll().resize();
//$(".messages").getNiceScroll().onResize();
}

function ClickedServiceProvider($this, calender_line, typing_icon){
     var provider = $this.html()
     var pk = $this.attr("id")
     $(".sent-span").remove();
     $("#chatID").append("<li class='sent service-provider-name msg-li' id="+pk+">"+provider+"</li>")
     setTimeout(function(){
     $("#chatID").append("<li class='typing-icon'>"+typing_icon+"</li>");
     AppendMessageBox();
     }, 500)
     setTimeout(function(){
     $(".typing-icon").remove();
     $("#chatID").append("<li class='replies msg-li'>"+calender_line+"<span class='open-datepicker'><i class='fa fa-calendar'></i></span></li>")

     },1500)
}