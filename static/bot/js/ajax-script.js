function save_title_name(id, name, page_url){
    if(name == ""){
        $("#name").css("border", "1px solid red")
        $(".error-chat-name").removeClass("hidden-element").text("Please enter chat title.")
        $(".save-title-loading").addClass("hidden-visible")
        return false;
     }
    $.ajax({
        url: page_url,
        data: {'id': id, 'name': name},
        dataType: 'json',
        success: function(data){
            $(".save-title-loading").addClass("hidden-visible")
            if(data['status'] == 'invalid'){
                alert("Invalid request. Please refresh and try again.")
            }
            else if(data["status"] == false){
                $("#name").css("border", "1px solid red")
                $(".error-chat-name").removeClass("hidden-element").text(data["message"])
            }
            else if(data['status'] == true){
                $(".instruction-box").removeClass("hidden-element")
                $(".update-chat-map").removeClass("hidden-element")
                $("#save-title").hide();

                $("#name").attr("disabled", true)
                $(".chat_name").val(name);
                $("#name").css("border", "1px solid #c2c2c2")
                $(".form-chat-title").val(data['pk'])
                if($(".error-chat-name").hasClass("hidden-element")){

                }
                else{
                    $(".error-chat-name").addClass("hidden-element")
                }
                $(".chat-title-created").removeClass('hidden-element')
            }
        },
        error: function(data){
            $(".save-title-loading").addClass("hidden-visible")
            alert("Something went wrong. Please refresh and try again.")
        }

     });
     $(".question-type-list").addClass('title-saved-ok')
}

function CreateSlotForm(form, page_url){
$.ajax({
         data: form.serialize(),
         type: 'post',
         url: page_url,
         success: function(data) {
             if(data['status'] == true){
             $(".providers-slot").html(data['html'])
             $('[data-toggle="tooltip"]').tooltip()
             $('.select-day-drop-down').selectpicker();
             }
             else{
                 form.find(".error-list").removeClass("hidden-element").html(data['message'])
             }
         },
         error: function(data){
         alert("Something went wrong. Please refresh and try again.")
         }
     });
     return false;
}

function NextQuestionAjax(view_url, pk, lang, main_type, child, number, option_child, option_number){
    var data = {'title': pk, 'lang': lang, 'main_type': main_type,
                'child': child, 'number': number, 'option_child': option_child, 'option_number': option_number}
    $.ajax({
        url : view_url,
        dataType : 'json',
        data : data,
        success: function(data){
            if(data['status'] == 'end_chat'){
            $(".typing-icon").remove()
            $(".end-chat-div").removeClass("hidden-element")
            AppendMessageBox()
            }
            else if(data['status'] == true){
                $(".typing-icon").remove()
                var append_li = "<li class='replies msg-li'></li>"
                $("#chatID").append(append_li)
                $("#chatID").find("li.replies:last").append(data["html"])
                    $('.messages').animate({ scrollTop: $(append_li).offset().top }, 1000);
                AppendMessageBox()
                if(data['is_option'] == false){

                    $(".wrap #chat-new-plot-message-input").removeClass("hidden-element").focus()
                    $(".wrap #chat-new-plot-message-submit").show()
                    $(".wrap #input-submit").attr('data-title-pk', data['title-pk'])
                }
            }
            else if(data['status'] == false){
            alert(data['message'])
            }
        },
        error: function(data){
        alert("Something went wrong. Please try again.")
        },
    });
}

function BookAppointment(title, page_url, language, pk, typing_icon){
    $(".sent-span").remove();
    $("#chatID").append("<li class='sent msg-li'>"+title+"</li>")
    setTimeout(function(){$("#chatID").append("<li class='typing-icon'>"+typing_icon+"</li>");
    AppendMessageBox()
    }, 500)

    setTimeout(function(){
    $.ajax({
    url : page_url,
    dataType: 'json',
    data: {'lang': language, 'pk': pk},
    success: function(data){
        $(".typing-icon").remove();
        $("#chatID").append("<li class='replies msg-li'>"+data['service_provider_line']+' '+ data['service_provider']+":</li>")
        if(data['status'] == true){
            $.each(data['providers'], function(i, obj) {
              $(".replies:last").append("<button class='sent-span btn btn-primary provider-list' id="+i+">"+obj+"</button>")
            });
            AppendMessageBox()
        }
        else if(data['status'] == false){
        alert(data['message'])
        }
    },
    error: function(data){
     alert("Something went wrong. Please try again.")
    }
    });
    }, 1500)
}

function AfterDateSelect(date, page_url, language, typing_icon){
    $("#chatID").append("<li class='sent msg-li' id='selected-date'>"+date+"</li>")
    AppendMessageBox();
    var pk = $(".service-provider-name").attr("id")
    setTimeout(function(){$("#chatID").append("<li class='typing-icon'>"+typing_icon+"</li>");
    AppendMessageBox();
    },500)
    setTimeout(function(){
    $.ajax({
    url: page_url,
    dataType: "json",
    data: {"pk": pk, "date": date, 'lang': language},
    success: function(data){
    if(data['status'] == true){
        $(".typing-icon").remove()
        $("#chatID").append("<li class='replies msg-li'>"+data['get_slot_line']+"</li>")
        $.each(data['slots'], function(i, obj) {
              $(".replies:last").append("<button class='sent-span btn btn-primary slot-list' id="+i+">"+obj+"</button>")
            });
        AppendMessageBox()
        }
    },
    error: function(data){
    alert("Something went wrong. Please try again.")
    }

    })
    }, 1500)
}

function GetProviderDetail(pk, page_url){
    $.ajax({
        url: page_url,
        dataType: "json",
        data: {'pk': pk},
        success: function(data){
            if(data['status'] == true){
                $(".providers-slot").html(data['html'])
                $('[data-toggle="tooltip"]').tooltip()
                $('.select-day-drop-down').selectpicker();
            }
        },
        error: function(data){
            alert("Something went wrong. Please refresh and try again.")
        }
    })
}

function CreateServiceProviderForm(form, page_url){
$.ajax({
         data: form.serialize(),
         type: 'post',
         url: page_url,
         success: function(data) {
             if(data['status'] == true){
             $(".service-provider-block").html(data['html'])
             $(".providers-slot").html(data['html2'])
             $('[data-toggle="tooltip"]').tooltip()
             $('.select-day-drop-down').selectpicker();
             }
             else{
                 form.find(".error-list").removeClass("hidden-element").html(data['message'])
             }
         },
         error: function(data){
         alert("Something went wrong. Please refresh and try again.")
         }
     });
     form.find(".provider-name").val("");
     form.find(".provider-name").focus();
     return false;

}

function ChangeProviderState(pk, name, page_url){
    $.ajax({
        url: page_url,
        data: {"pk": pk, "name": name},
        dataType: "json",
        success: function(data){
//            $(".loading-image").addClass("hidden-element")
            if(data['status'] == true){
                 $(".providers-slot").html(data['html'])
                 $('[data-toggle="tooltip"]').tooltip()
                 $('.select-day-drop-down').selectpicker();
            }
            if(data['status'] == false){
                alert(data['message'])
            }
        },
        error: function(data){
//            $(".loading-image").addClass("hidden-element")
            alert("Something went wrong.Please refresh and try again")
        }
    })
}

function RemoveQuestion(pk, page_url){
    $.ajax({
        url: page_url,
        dataType: "json",
        data: {'question_pk': pk},
        success: function(data){
            if(data['status'] == 'invalid'){
                alert(data['message'])
            }
            else if(data['status'] == true){
                $(".question-collection").html(data['html'])
                AddParentInSavedQuestion()
            }
        },
        error: function(data){
            alert("Something went wrong. Please refresh and try again.")
        }
    });
}

function AppendMessageBox(){
        $(".messages").stop().animate({ scrollTop: $(".messages")[0].scrollHeight}, "fast");
//    $(".messages").getNiceScroll().resize();
//$(".messages").getNiceScroll().onResize();
}

function TestChatReply(question, dir_name, page_url, typing_icon){
    $("#chatID").append("<li class='sent msg-li'>"+question+"</li>")
    AppendMessageBox()
    setTimeout(function(){
    $("#chatID").append("<li class='typing-icon'>"+typing_icon+"</li>");
    AppendMessageBox();
    }, 500)
    $("#chat-message-input").val("")
    $("#chat-message-input").hide()
    $("#chat-message-submit").hide()

   setTimeout(function(){
    $.ajax({
        url: page_url,
        data: {"question": question, "dir_name": dir_name},
        dataType: "json",
        success: function(data){
            debugger;
             $(".typing-icon").remove()
            if(data['status'] = true){

                if (data['get_answer'] == 'fail') {
                   $("#talk_or_not").find("p.text").html(data['reply'])
                    $("#talk_or_not").show();
                } else {
                   $("#chatID").append("<li class='replies msg-li'>"+data['reply']+"</li>")
                    $("#chat-message-input").show()
                    $("#chat-message-submit").show()
                    $("#chat-message-input").focus()
                }
                AppendMessageBox()
            }
        },
        error: function(data){
        alert("Something went wrong. Please try again.")
        }
    })
    }, 700)
}

function BookAppointmentYes(page_url, user_uid){
    var selected_date = $("#selected-date").text()
    var selected_slot = $(".selected-slot").attr("id")
    var selected_slot_time = $(".selected-slot").text()
    var selected_provider = $(".service-provider-name").attr("id")
    $("#book-appointment-div").hide();
    $("#please-wait-p").show();
    $.ajax({
        url: page_url,
        dataType: "json",
        data: {"selected_date": selected_date, "selected_slot": selected_slot, "u_id": user_uid, "slot_time": selected_slot_time, "selected_provider": selected_provider},
        success: function(data){
        $("#please-wait-p").hide();
        if(data['status'] == true){
            $("#send-mail-confirm").show();
        }
        else if(data['status'] == false){
            alert("Something went wrong. Please try again.")
        }
        },
        error: function(data){
            $("#please-wait-p").hide();
            alert("Something went wrong. Please try again.")
        }
    })
}

function ChangePassword(form, page_url){
     $.ajax({
         data: form.serialize(),
         type: 'post',
         url: page_url,
         success: function(data) {
             if(data['status'] == false){

             $(".form-error").html(data['message'])

             }
             else{
                 alert("password has been changed successfully.")
                 location.reload();
             }
         },
         error: function(data){
         alert("Something went wrong. Please refresh and try again.")
         }
     });
}

function RemoveNotification(note_type, secret_key, page_url, $this){
    $.ajax({
         data: {"note_type": note_type, "secret_key": secret_key},
         url: page_url,
         dataType: "json",
         success: function(data) {

         },
         error: function(data){
            alert("Something went wrong. Please refresh and try again.")
         }
     });
     if ($(this).parent().find("span.notify_status").hasClass("notification") ){
        $(this).parent().find("span.notify_status").removeClass("notification")
        $(this).parent().find("span.notify_status").html("")
    }
}

function AddBotFormFunction(page_url, $this){
    $(".bot-form").addClass("hidden-element")
    $(".bot-list").removeClass("hidden-element")
    $(".cancel_button").addClass("hidden-element")
    $(".add_bot_button").removeClass("hidden-element")
    var pk = $this.attr("data-pk")
    $.ajax({
        url: page_url,
        dataType: 'json',
        data: {'user_pk': pk},
        success: function(data){
            if(data['status'] == true){
                $this.addClass("hidden-element")
                $this.siblings(".cancel_button").removeClass("hidden-element")
                $this.parent().siblings(".bot-td").find(".bot-list").addClass("hidden-element")
                $this.parent().siblings(".bot-td").find(".bot-form").html(data['html']).removeClass("hidden-element")
                $('.select-bot').selectpicker();
            }
            else if(data['status'] == false){
                alert(data['message'])
            }
        },
        error:function(data){
            alert("Something went wrong. Please refresh and try again.")
        }
    })
}