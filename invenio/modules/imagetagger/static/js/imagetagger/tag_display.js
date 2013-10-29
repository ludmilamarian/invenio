var nb_tags = -1;
var nb_faces = 0;
var tags = new Array();
var faces = new Array();
var current_face = -1;
var current_tag = -1;
var isFace = false;
var current_title = '';
var class_ids = {'image': '#imageMap', 'mapper': '#mapper', 'tag': ".tagged", 'tag_box': '.tagged_box', 'tag_title': '.tagged_title', 'tag_type': '.type', 'face': '.tagged2', 'delete': '.delete', 'add_panel': '#form_panel_add', 'modif_panel': '#form_panel_modify', 'tag_block': '#planetmap'}

function Tag(id, title, x, y, w, h, type){
    this.id = id;
    this.title = title;
    this.x = x;
    this.y = y;
    this.w = w;
    this.h = h;
    this.type = type;
}

$(document).ready(function() {  
    
    var get_image_width = function(){
        image_width = $(class_ids['image']).css('width');
    }

    //get the previous tags from the html content
    var fill_tags_tab =function(){
        var res = $(class_ids['tag']);
        for(var i=0; i<res.length; i++){
            var tag = $(res[i]);
            var pos_x = tag.css('left');
            pos_x = pos_x.substr(0,pos_x.length-2);
            var pos_y = tag.css('top');
            pos_y = pos_y.substr(0,pos_y.length-2);
            var pos_width = tag.css('width');
            pos_width = pos_width.substr(0,pos_width.length-2);
            var pos_height = tag.css('height');
            pos_height = pos_height.substr(0,pos_height.length-2);
            var id = tag.find(class_ids["tag_box"]).attr('id').substr(3);
            var t = $.trim($(res[i]).find(class_ids['tag_title']).text());
            var tag_type = $(res[i]).find(class_ids["tag_type"]).text()
            tags['tag'+id] = new Tag(id, t, pos_x, pos_y, pos_width, pos_height, tag_type);
        }
    }

    size_tags = $(this).find(class_ids['tag']).length;
    current_tag = nb_tags;
    if(size_tags > 0){
        fill_tags_tab();
    }
    //get the face suggestions
    var fill_faces_tab =function(){
        var res = $(class_ids['face']);
        for(var i=0; i<res.length; i++){
            var tag = $(res[i]);
            var pos_x = tag.css('left');
            pos_x = pos_x.substr(0,pos_x.length-2);
            var pos_y = tag.css('top');
            pos_y = pos_y.substr(0,pos_y.length-2);
            var pos_width = tag.css('width');
            pos_width = pos_width.substr(0,pos_width.length-2);
            var pos_height = tag.css('height');
            pos_height = pos_height.substr(0,pos_height.length-2);
            var t = $.trim($(res[i]).find(class_ids['tag_title']).text());
            faces['tag'+i] = new Tag(i, t, pos_x, pos_y, pos_width, pos_height, 'face');
        }
    }

    nb_faces = $(this).find(class_ids['face']).length;
    current_face = nb_faces;
    if(nb_faces > 0){
        fill_faces_tab();
    }

    //click for tagging --> a square appear
    $(class_ids['image']).click(function(e){
        hideTags();
        var image_left = $(this).offset().left;
        var click_left = e.pageX;
        var left_distance = click_left - image_left;

        var image_top = $(this).offset().top;
        var click_top = e.pageY;
        var top_distance = click_top - image_top;

        var mapper_width = $(class_ids['mapper']).width();
        var imagemap_width = $(class_ids['image']).width();

        var mapper_height = $(class_ids['mapper']).height();
        var imagemap_height = $(class_ids['image']).height();

        if((top_distance + mapper_height > imagemap_height) && (left_distance + mapper_width > imagemap_width)){
            $(class_ids['mapper']).css("left", (click_left - mapper_width - image_left  ))
            .css("top",(click_top - mapper_height - image_top  ))
            .css("width","100px")
            .css("height","100px")
            .show();
        }
        else if(left_distance + mapper_width > imagemap_width){
            $(class_ids['mapper']).css("left", (click_left - mapper_width - image_left  ))
            .css("top",top_distance)
            .css("width","100px")
            .css("height","100px")
            .show();

        }
        else if(top_distance + mapper_height > imagemap_height){
            $(class_ids['mapper']).css("left", left_distance)
            .css("top",(click_top - mapper_height - image_top  ))
            .css("width","100px")
            .css("height","100px")
            .show();
        }
        else{
            $(class_ids['mapper']).css("left",left_distance)
            .css("top",top_distance)
            .css("width","100px")
            .css("height","100px")
            .show();
        }


        $(class_ids['mapper']).resizable({ containment: "parent" });
        $(class_ids['mapper']).draggable({ containment: "parent" });
        
    });


});

var hideMapper = function(){
    $(class_ids['mapper']).hide();
}

//tag display 
$(class_ids['tag']).live("mouseover",function(){
    if($(this).find(class_ids['delete']).length == 0){
        $(this).find(class_ids['tag_box']).css("display","block");
        $(this).css("border","2px solid #EEE");
        $(this).find(class_ids['tag_title']).css("display","block");
    }


});

//tag hiding
$(class_ids['tag']).live("mouseout",function(){
    if($(this).find(class_ids['delete']).length == 0){
        $(this).find(class_ids['tag_box']).css("display","none");
        $(this).css("border","none");
        $(this).find(class_ids['tag_title']).css("display","none");
    }


});

//face display
$(class_ids['face']).live("mouseover",function(){
    if($(this).find(class_ids['delete']).length == 0){
        $(this).find(class_ids['tag_box']).css("display","block");
        $(this).css("border","2px solid #EEE");
        $(this).find(class_ids['tag_title']).css("display","block");
    }


});

//face hiding
$(class_ids['face']).live("mouseout",function(){
    if($(this).find(class_ids['delete']).length == 0){
        $(this).find(class_ids['tag_box']).css("display","none");
        $(this).css("border","none");
        $(this).find(class_ids['tag_title']).css("display","none");
    }


});

//tag modification
$(class_ids['tag']).live("click",function(){
    $(this).find(class_ids['tag_box']).html("<img src='"+del+"' class='delete' value='Delete' onclick='deleteTag(this)' />\n\
<img src='"+save+"' class='save' onclick='editTag(this);' value='Save' />");        

    var img_scope_top = $(class_ids['image']).offset().top + $(class_ids['image']).height() - $(this).find(class_ids['tag_box']).height();
    var img_scope_left = $(class_ids['image']).offset().left + $(class_ids['image']).width() - $(this).find(class_ids['tag_box']).width();

    $(this).draggable({ containment:[$(class_ids['image']).offset().left,$(class_ids['image']).offset().top,img_scope_left,img_scope_top]  });

});

//face suggestion modification
$(class_ids['face']).live("click",function(){
    console.log("clickonface");
    hideTags();
    $(this).find(class_ids['tag_box']).css("display","block");
    $(this).css("border","2px solid #EEE");
    $(this).find(class_ids['tag_title']).css("display","block");
    isFace = true;
     
    $(this).find(class_ids['tag_box']).html("<img src='"+del+"' class='delete' value='Delete' onclick='deleteFace(this)' />\n\
<img src='"+save+"' class='save' onclick='editTag(this);' value='Save' />");

    var img_scope_top = $(class_ids['image']).offset().top + $(class_ids['image']).height() - $(this).find(class_ids['tag_box']).height();
    var img_scope_left = $(class_ids['image']).offset().left + $(class_ids['image']).width() - $(this).find(class_ids['tag_box']).width();

    $(this).draggable({ containment:[$(class_ids['image']).offset().left,$(class_ids['image']).offset().top,img_scope_left,img_scope_top]  });

});

//called after the tag creation form desappears
var addTag = function(){
    var position = $(class_ids['mapper']).position();

    var pos_x = position.left;
    var pos_y = position.top;
    var pos_width = $(class_ids['mapper']).width();
    var pos_height = $(class_ids['mapper']).height();
    var type = $(class_ids['add_panel']+' #tag_type option:selected').val();

    $(class_ids['tag_block']).append('<div class="tagged"  style="width:'+pos_width+'px;height:'+
        pos_height+'px;left:'+pos_x+'px;top:'+pos_y+'px;" ><div class="tagged_box" id="tag'+nb_tags+'" style="width:'+pos_width+'px;height:'+
        pos_height+'px;display:none;" ></div><div id="tag'+nb_tags+'t" class="tagged_title" style="top:'+(pos_height+5)+'px;display:none;" id="'+$("#title").val()+'" >'+
        $("#title").val()+'</div><div id="type" style="display:none;">'+type+'</div></div>');
    tags['tag'+nb_tags] = {title:$("#title").val(), x:pos_x, y:pos_y, w:pos_width, h:pos_height, type:type};
    $(class_ids['mapper']).hide();
    $("#title").val('');
    $(class_ids['add_panel']).hide();
    
    nb_tags = nb_tags - 1;

};

//same as above but for a face suggestion
var addFace = function(new_title){
    var position = $('#'+current_tag).parent().position();
    var pos_x = position.left;
    var pos_y = position.top;
    var pos_width = $('#'+current_tag).parent().width();
    var pos_height = $('#'+current_tag).parent().height();
    var type = $(class_ids['add_panel']+' #tag_type option:selected').val();
    $(class_ids['tag_block']).append('<div class="tagged"  style="width:'+pos_width+'px;height:'+
        pos_height+'px;left:'+pos_x+'px;top:'+pos_y+'px;" ><div class="tagged_box" id="tag'+nb_tags+'" style="width:'+pos_width+'px;height:'+
        pos_height+'px;display:none;" ></div><div id="tag'+nb_tags+'t" class="tagged_title" style="top:'+(pos_height+5)+'px;display:none;" id="'+$("#title").val()+'" >'+
        new_title+'</div><div id="type" style="display:none;">'+type+'</div></div>');
    tags['tag'+nb_tags] = {title:new_title, x:pos_x, y:pos_y, w:pos_width, h:pos_height, type:type};
    $(class_ids['mapper']).hide();
    $("#title").val('');
    $(class_ids['add_panel']).hide();
    
    nb_tags = nb_tags - 1;

};

var saveModifications = function(obj){
    $(class_ids['mapper']).hide();
    var new_title = $(class_ids['modif_panel']).find("#title").val();
    var type = $(class_ids['modif_panel']).find("#tag_type option:selected").val();
    if(isFace){
        addFace(new_title);
        deleteFace(null);
    }else{                
        $("#"+current_tag+"t").text(new_title);
        tags[current_tag].title = new_title;       
        $("#"+current_tag+"t").parent().find('#type').text(type);
        tags[current_tag].type = type;               
    }
    $(class_ids['modif_panel']).hide();
    isFace = false;
};

//form for adding a tag
var openDialog = function(){
    $(class_ids['add_panel']).fadeIn("slow");
};

//form for modifying a tag
var openDialog2 = function(obj){
    var title = "";
    var type = 'face';
    if(!isFace){
        title = tags[current_tag].title;
        type = tags[current_tag].type;
    }
    $(class_ids['modif_panel']).find("#title").val(current_title);
    $(class_ids['modif_panel']).find("#tag_type option:selected").removeAttr('selected');
    $(class_ids['modif_panel']).find("#tag_type option[value='"+type+"']").attr('selected','selected');
    $(class_ids['modif_panel']).fadeIn("slow");
};

//tags displayed all at once
var showTags = function(){
    $(class_ids['tag_box']).css("display","block");
    $(class_ids['tag']).css("border","2px solid #EEE");
    $(class_ids['face']).css("border","2px solid #EEE");
    $(class_ids['tag_title']).css("display","block");
    $(class_ids['tag_title']).css("display","block");
};

//tags hidden
var hideTags = function(){
    $(class_ids['tag_box']).css("display","none");
    $(class_ids['tag']).css("border","none");
    $(class_ids['face']).css("border","none");
    $(class_ids['tag_title']).css("display","none");
    $(class_ids['tag_title']).css("display","none");
};

//when tagging is done, the page is refreshed, the data is sent
var sendTags = function(){
    var form = document.createElement("form");
    form.setAttribute("method", "post");
    var ac = '';
    if(action != -1)
        ac = '/'+action;
    form.setAttribute("action", "/imagetagger"+current_url+ac);
    nb_tags2 = 0;
    for(var i in tags){
        var tag = tags[i];
         if(tag.title != undefined){
            var hiddenField = document.createElement("input"); 
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", i);
            hiddenField.setAttribute("value", tag.title+';'+tag.x+';'+tag.y+';'+tag.w+';'+tag.h+';'+tag.type+';'+image_width);
            form.appendChild(hiddenField);
            nb_tags2++;
        }
    }
    var hiddenField = document.createElement("input"); 
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", "nb_tags");
            hiddenField.setAttribute("value", nb_tags2);
            form.appendChild(hiddenField);
    document.body.appendChild(form);
    form.submit();
    
};

//after a click on the save button of a tag
var editTag = function(obj){
    current_tag = $(obj).parent().attr("id");
    current_title = $.trim($(obj).parent().parent().find(class_ids['tag_title']).text());
    openDialog2(obj);  
    $(obj).parent().parent().draggable( 'disable' );
    $(obj).parent().parent().removeAttr( 'class' );
    if(isFace){
        $(obj).parent().parent().addClass( 'tagged2' );

    }else{
        $(obj).parent().parent().addClass( 'tagged' );
    }

    $(obj).parent().parent().css("border","none");
    $(obj).parent().css("display","none");
    $(obj).parent().parent().find(class_ids['tag_title']).css("display","none");
    $(obj).parent().html('');   
}

//after clicking on the delete button of a tag
var deleteTag = function(obj){
    current_tag = $(obj).parent().attr('id');
    tags[current_tag] = {};
    $(obj).parent().parent().remove();
};

var deleteFace = function(obj){
    if(obj!=null){
        current_tag = $(obj).parent().attr('id');
        $(obj).parent().parent().remove();
    }else{
        $('#'+current_tag).parent().remove();
    }
    faces[current_tag] = {};
}