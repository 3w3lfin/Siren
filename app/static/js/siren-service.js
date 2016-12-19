$(document).ready(function () {  
    $(".removeButton").click(function(){
        var id = $(this).attr("data-catid");
        var service = $(this).attr("data-ser");
        $.get('/app/show_service/' + service, {command: "remove", com_id: id}, function(){
               $('#div_'+id).hide();
        });
    });
    
    $(".removeButtonParamGroup").click(function(){
        var id = $(this).attr("data-catid");
        var service = $(this).attr("data-ser");
        $.get('/app/show_service/' + service, {command: "remove_group", pargr_id: id}, function(){
               $('#panel_'+id).hide();
        });
    });
    
    $(".removeButtonParam").click(function(){
        var id = $(this).attr("data-catid");
        var service = $(this).attr("data-ser");
        $.get('/app/show_service/' + service, {command: "remove_param", par_id: id}, function(){
               $('#tr_'+id).hide();
        });
    });

    $(".removeInit").click(function(){
        var id = $(this).attr("data-catid");
        var service = $(this).attr("data-ser");
        $.get('/app/show_service/' + service, {command: "remove_init", init_id: id}, function(){
               $('#init_'+id).hide();
        });
    });
    
    $(".removeCode").click(function(){
        var id = $(this).attr("data-catid");
        var service = $(this).attr("data-ser");
        $.get('/app/show_service/' + service, {command: "remove_init", init_id: id}, function(){
               $('#code_'+id).hide();
        });
    });
    
    $(".removeShare").click(function(){
        var id = $(this).attr("data-catid");
        var service = $(this).attr("data-ser");
        $.get('/app/show_service/' + service, {command: "remove_share", userser_id: id}, function(){
            $('#removeshare_'+id).hide();
        });
    });
    
    $(".editButton").click(function(){
        var val = $(this).attr("data-catid");
        $(val+"one").toggle();
        $(val+"two").toggle();
    });
    
     $('#my_radio_box').change(function(){
        selected_value = $("input[name='my_options']:checked").val();
        alert(selected_value);
    });
});
