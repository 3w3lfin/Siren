// script siren is freely distributable under the terms of an MIT-style license.

//MENU
$(document).ready(function () {
    $('label.tree-toggler').parent().children('ul.tree').toggle(0);
});

$(document).ready(function () {
    $('label.tree-toggler').click(function () {
        $(this).parent().children('ul.tree').toggle(300);
    });
    $('#blindLeftToggle').on('click', function(){
      var $this = $(this);
      if ($this.hasClass('open')) {
        $this.animate({
          left : '0px'
        }, 500).removeClass('open');
        $( "#menu" ).animate({
          left : '-180px'
        }, 500).removeClass('open');
      } else {
        $this.animate({
          left : '180px'
        }, 500).addClass('open');
        $( "#menu" ).animate({
          left : '0px'
        }, 500).addClass('open');
      }
    });        
});


$(document).ready(function () {    
    $('#out').slideDown("slow");
    
    $('.show').click(function(){      
        $('#out').slideUp("slow");
        var tmp1 = "/app/show_project/";
        var tmp2 = $(this).text();
        redirectURL = tmp1 + tmp2; 
        redirectTime = "1000";
        
        setTimeout("location.href = redirectURL;",redirectTime);
        
    });
    
    $(".down").click(function(){
            var str = $(this)[0].getAttribute("data");
            var target = $("#" + str);
            $(".content").not(target).slideUp("slow");
            target.slideToggle("slow").toggleClass("active");
            $('.down').not(this).removeClass('active');
            return false;
        }); 
        
         
    $(".down2").click(function(){
            var target = $("#" + $(this).text());
            $(".content").not(target).slideUp("slow");
            target.slideToggle("slow").toggleClass("active");
            $('.down').not(this).removeClass('active');
            return false;
    }); 
    
    
    $(".show_button").click(function(){
        var com_id = $(this).attr("data-catid");
        var y = $(this).attr("id");
        var z = y.substring(y.length - 4);
        
        $.get('/app/show_project/{{ project.id }}', {command: z, com_id: com_id}, function(update_com){
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
    $('a[data-toggle=modal]').click(function () {
        var path = $(this).attr("data-path");
        path = path.substring(path.indexOf('/')+1);
        path = path.substring(path.indexOf('/')+1);
        path = "{{ baseUrl }}" + path;
        $('#path').attr('src', path); 
        $('#data').attr('data', path); 
        $('#frame').attr('src', path); 
    });
    
    
    
    var showElement = function(el, display) {
        el.style.display = display ? '' : 'none';
    };

    $('.vert_nav').click(function(e) {
        e.preventDefault();
        $('.vert_nav').removeClass('active');
        $(this).addClass('active');
        var hide = document.getElementsByClassName('vert_content');
        for (var i = 0, ii = hide.length; i < ii; i++) {
            showElement(hide[i], false);
        };
        var id = $(this).attr("data-show");
        if (id == "add_new") {
            window.location = "/app/new_service"
        }
        var to_show = document.getElementById(id);
        showElement(to_show, true);
        
    });
    
    $('a[data-toggle="tooltip"]').tooltip({
        html: true,
        animated: 'fade',
        placement: 'right'
        
    });
    
    $('.no-collapsable').on('click', function (e) {
        e.stopPropagation();
    });
    
});

function show_params(source) {
    var tr = source.parentNode;
    try {
         $("div").remove(".myclass");
    }catch (e) {}
    
    var div = document.createElement("div");
    div.setAttribute('class', 'myclass');
    tr.appendChild(div);
    param_id = source.value
    if (param_id != "") {
        $(".myclass").load( "my_div.html", { param_id: param_id}, function() {});
    }
}

function toggle(source) {
    checkboxes = document.getElementsByName('stay');
    if (checkboxes[0].checked) {
        var t = false;
    } else {
        var t = true;
    }

    for(var i=0, n=checkboxes.length; i<n; i++) {
        checkboxes[i].checked = t;
    }
}

function toggleTarget(target) {
    var target = $("#" + target);
    target.slideToggle(1500).toggleClass("active");
    $('.down').not(this).removeClass('active');
}



