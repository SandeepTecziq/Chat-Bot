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

function AfterDateSelect(date, page_url, language, pk){
    $(".msg-container").append("<div class='sent-msg msg-txt selected-date'>"+date+"</div>")
    setTimeout(function(){
    $(".ticontainer").removeClass("d-none")
    AppendMessageBox();
    }, 100)
    setTimeout(function(){
    $.ajax({
    url: page_url,
    dataType: "json",
    data: {"pk": pk, "date": date, 'lang': language},
    success: function(data){
    	$(".ticontainer").addClass("d-none")
		if(data['status'] == true){
			$(".msg-container").append(data['html'])
			AppendMessageBox()
		}
		else{
     		$("#chatID").append("<li class='replies msg-li'>"+data['message']+"<span class='open-datepicker'><i class='fa fa-calendar'></i></span></li>")
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

function AppendMessageBox(){
        $(".chat-body").stop().animate({ scrollTop: $(".chat-body")[0].scrollHeight}, "fast");
        $(".chat-nrml-box").stop().animate({ scrollTop: $(".chat-nrml-box")[0].scrollHeight}, "fast");
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

function AddBotReply(question_data, page_url){
    var localStorage = window.localStorage;
	$(".msg-box").find(".btn-submit").addClass("disabled")
	$(".msg-box").find(".msg-input").prop("disabled", true).val("")
	$(".msg-container").append("<div class='sent-msg msg-txt'>"+question_data['question']+"</div>")
    AppendMessageBox();
    setTimeout(function(){$(".ticontainer").removeClass("d-none")}, 100)
	$.ajax({
		url: page_url,
		data: data,
		dataType: 'json',
		success: function(data){
			if(data['status'] == true){
				setTimeout(function(){
					$(".ticontainer").addClass("d-none")
					if (data['get_answer'] == 'fail') {
						$(".continue-chat").find("p").text(question_data['backup_line'])
						$(".continue-chat").removeClass("d-none");
					} else {
					    $(".msg-container").append("<div class='reply-msg msg-txt'>"+data['reply']+"</div>")
						$(".msg-box").find(".msg-input").prop("disabled", false).focus();
	                    $(".msg-box").find(".btn-submit").removeClass("disabled")
					}
					$(".chat-body").animate({
						scrollTop: $(document).height()
					}, "fast");
				},2000);
			}
			else{
				alert(data['message'])
			}
		},
		error: function(data){
			$(".ticontainer").addClass("d-none")
		}
	})
}

function SortQuestions(l_sort, page_url){
    pk_list = l_sort.join(",");
    $.ajax({
        url: page_url,
        dataType: "json",
        data: {'array': pk_list},
        success: function(data){
            if(data['status'] == true){
                location.reload();
            }
        },
        error: function(data){
            alert("Something went wrong. Please refresh and try again")
        },
    })
}

function GetNextQuestion(title_pk, question_pk, is_option){
	page_url = "/get_next_question/"+title_pk+"/"+question_pk+"/"+is_option+"/"
	$(".btn-option").remove()
    $(".chat-body").animate({
        scrollTop: $(document).height()
    }, "fast");
    setTimeout(function(){$(".ticontainer").removeClass("d-none")}, 100)
	$.ajax({
		url: page_url,
		data: {},
		dataType: "json",
		success: function(data){
			setTimeout(function(){
				$(".ticontainer").addClass("d-none")
				if(data['status'] == true){
					$(".msg-container").append(data['html'])
					AppendMessageBox()
					if(data['ans_type'] == 'T'){
						$(".msg-box").find(".msg-input").prop("disabled", false).focus();
						$(".btn-map").removeClass("disabled")
						$(".btn-map").attr("data-title", data['title_pk'])
						$(".btn-map").attr("data-pk", data['question_pk'])
					}
					else if(data['ans_type'] == 'I'){
						GetNextQuestion(data['title_pk'], data['question_pk'], 'incorrect')
					}
				}
				else if(status['status'] == false){
					$(".chat-map-error").removeClass("d-none")
					$(".chat-map-error").find("p").text(data['message'])
					AppendMessageBox()
				}
				else if(data['status'] == 'last'){
					$(".chat-map-last").removeClass("d-none")
					$(".chat-map-last").find("p").text(data['message'])
					AppendMessageBox()
				}
			},2000);
		},
		error: function(data){
			setTimeout(function(){
				$(".ticontainer").addClass("d-none")
					$(".chat-map-error").removeClass("d-none").text("Something went wrong. Please try again.")
			},2000);
		},
	})
}

function BookSelectedSlot(page_url, slot_pk, time, u_id){
    $(".approve-booking-yes").addClass("d-none")
    $(".approve-booking-no").addClass("d-none")
    $(".book-wait").removeClass("d-none")
	$.ajax({
		url: page_url,
		data: {'slot_pk': slot_pk, 'time': time, 'u_id': u_id},
		dataType: 'json',
		success: function(data){
		    if(data['status'] == true){
                $(".chat-map-error").addClass("d-none")
                $(".booking-confirmation-box").addClass("d-none")
                $(".booking-confirmed").removeClass("d-none")
                $(".booking-confirmed").find("p").text(data['message']).removeClass("d-none")
                $(".msg-input").prop("disabled", false)
                $(".btn-auto-bot").removeClass("disabled")
			}
			else{
				$(".booking-confirmation-box").addClass("d-none")
                $(".booking-confirmed").addClass("d-none")
			    $('.chat-map-error').removeClass('d-none')
			    $('.chat-map-error').find('p').text(data['message'])
			}
		},
		error: function(data){
		    $(".approve-booking-yes").addClass("d-none")
            $(".approve-booking-no").addClass("d-none")
            $(".book-wait").removeClass("d-none")
			$(".chat-map-error").removeClass("d-none").text("Something went wrong. Please try again.")
		}
	})
}

function NotifyEmp(key, user_id, emp_id, ws_scheme, msg){
	var alertEmployeeSocket = new ReconnectingWebSocket(
    ws_scheme + window.location.host +
    '/ws/alert_employee/'  + key +'/'+ emp_id + '/');
	alertEmployeeSocket.onopen = function(e){
		alertEmployeeSocket.send(JSON.stringify({
			'last_ques': msg,
			'user_id': user_id,
			'emp_id': emp_id,
    	}));
    };
}

function ConnectToEmployee(page_url, ws_scheme, parent_secret_key, u_id){
	$.ajax({
		url: page_url,
		data: {},
		dataType: "json",
		success: function(data){
			if(data['status'] == true){
				$(".human-chat-loading").addClass("d-none")
				$(".no-online-msg").addClass("d-none")
				$(".chat-nrml").removeClass("d-none")
				msg = "New Chat"
				NotifyEmp(parent_secret_key, u_id, data['emp_pk'], ws_scheme, msg)
				$(".active-employee").val(data['emp_pk'])
			}
			else if(data['status'] == false){
			    $(".chat-nrml").addClass("d-none")
				$(".human-chat-loading").addClass("d-none")
				$(".no-online-msg").removeClass("d-none")
			}
			else{
			 alert(data['message'])
			}
		},
		error: function(data){
			alert("Something went wrong. Please try again.")
		}
	})
}

function LeaveHumanChat(emp_id, page_url, parent_secret_key, ws_scheme, u_id){
	$.ajax({
		url: page_url,
		data: {'emp_id': emp_id},
		dataType: 'json',
		success: function(data){
			$(".active-employee").val("")
			msg = "End Chat"
			NotifyEmp(parent_secret_key, u_id, emp_id, ws_scheme, msg)
		},
		error: function(data){}
	})
}