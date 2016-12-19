$(document).ready(function(){
    $('.show_btn').click(function () {
        var path = $(this).attr("data-path");
        path = path.substring(path.indexOf('/')+1);
        path = path.substring(path.indexOf('/')+1);
        path = "/static/" + path;
        $('#path').attr('src', path); 
        $('#data').attr('data', path); 
        $('#frame').attr('src', path); 
    });
    
    $('.download_btn').click(function () {
        var path = $(this).attr("data-path");
        path = path.substring(path.indexOf('/')+1);
        path = path.substring(path.indexOf('/')+1);
        path = "/static/" + path;
        document.getElementById('iframe_del').src = path;
    });
    
    $(".remove").click(function(){
        var id = $(this).attr("data-catid");
        var comm = $(this).attr("data-comm");
        var file = $(this).attr("data-file");
        if(comm == "ext") {
            $.get('/app/show_file/' + file, {command: "removeext", ext_id: id}, function(){});
        } else if(comm == "removeproject") {
            $.get('/app/show_file/' + file, {command: "removeproject", project_id: id}, function(){
                $('#remove_pro_'+id).hide(); 
            });
        } else if(comm == "group") {
            $.get('/app/show_file/' + file, {command: "removegroup", group_id: id}, function(){});
        } else if(comm = "remove_user") {
            $.get('/app/show_file/' + file, {command: "remove", userfile_id: id}, function(){
                $('#remove_'+id).hide();
            });
        }
    });
        
    $(".removeButton").click(function(){
        var id = $(this).attr("data-catid");
        var file_id = $(this).attr("data-file");
        $.get('/app/show_file/' + file_id, {command: "removebutton", com_id: id}, function(){
               $('#div_'+id).hide();
           });
    });
    
    
    $(".editButton").click(function(){
        var me = $(this);
        $(me.val()+"one").toggle();
        $(me.val()+"two").toggle();
    });
    
    $(".show_button").click(function(){
        var com_id = $(this).attr("data-catid");
        var file_id = $(this).attr("data-file");
        var y = $(this).attr("id");
        var z = y.substring(y.length - 4);
        
        $.get('/app/show_file/' + file_id, {command: z, com_id: com_id}, function(update_com){
            var l = document.getElementById(y)
            if (z == "show") {
                l.setAttribute("id", com_id + "_hide");
                l.innerHTML = "Hide";
            } else {

                l.setAttribute("id",  com_id + "_show");
                l.innerHTML = "Show";
            }
        });
    });
    
    $('.vert_nav').click(function(e) {
        e.preventDefault();
        $('.vert_nav').removeClass('active');
        $(this).addClass('active');
        var hide = document.getElementsByClassName('vert_content');
        for (var i = 0, ii = hide.length; i < ii; i++) {
            showElement(hide[i], false);
        };
        var id = $(this).attr("data-show");
        var to_show = document.getElementById(id);
        showElement(to_show, true);
        
    });
});

var showElement = function(el, display) {
    el.style.display = display ? '' : 'none';
};
