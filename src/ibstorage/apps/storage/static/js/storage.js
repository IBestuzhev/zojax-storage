var blocks = ['login', 'filelist', 'fileupload', 'fileinfo', 'sharebox', 'publish', 'filedelete', 'flatpage', 'messages']
var filelist_directives = {
    '.emptyMsg' : 'emptyMsg',
    '.files li' :  {
        'file <- files' :{
            'a' : 'file.file',
            'a@href' : 'file.link',
            'a@rel' : 'address:#{file.link}',
            'em' : 'file.uploaded_at',
            '.@class+' : function (arg) { return arg.item.public?" public-file":""}
        }
    },
    '.pages option' : {
        'p <- pages' : {
            "@value" : 'p',
            "@selected" : function (arg) {return ((arg.pos+1) == arg.context.cur_page)?'selected' : ''},
            "." : 'p'
        }
    },
    '.pager@class' : function (arg) { return arg.context.pages.length > 1 ? '' : 'hidden'}
}
var fileupload_directives = {
    '.file-err' : 'errors.file',
    '.public-err' : 'errors.public'
}
var fileinfo_directives = {
    'h3' : '#{file}#{errorMsg}',
    '.actions li' : {
        'action <- actions' : {
            'a' : 'action.action',
            'a@href' : 'action.url',
            'a@target' : function (arg) {return (arg.item.local)?'':'_blank'},
            'a@rel' : function(arg) {return (arg.item.local)?('address:'+arg.item.url):''}
        }
    },
    '.actions@class+' : function(arg) {return (typeof arg.context.actions == 'undefined')?' hidden':''},
    '.details .field' : {
        'field <- info' : {
            'strong' : 'field.name',
            'span' : 'field.value'
        }
    },
    '.details@class+' : function(arg) {return (typeof arg.context.info == 'undefined')?' hidden':''}
}
var sharebox_directives = {
    '.link@value' : 'absolute_link',
    'a.back@href' : 'link',
    'a.back@rel' : 'address:#{link}',
    '.share-form@action' : 'action',
    '.form-content' : 'form',
    'h3' : 'file'
}
var publish_directives = {
    'h3' : 'file',
    '.back@href' : 'back_link',
    '.back@rel' : 'address:#{back_link}',
    'form@action' : 'action_link',
    '.status' : 'status'
}
var filedelete_directives = {
    'h3' : 'file',
    '.back@href' : 'back_link',
    '.back@rel' : 'address:#{back_link}',
    'form@action' : 'action_link'
}
var messages_directives = {
    '.msg-display' : {
        'msg <- ' : {
            '.' : 'msg.message',
            '@class+' : " #{msg.tags}"
        }
    }
}
var instructions_directives = {
    'h3 .username' : function(attr) { return attr.context.username || 'Guest' },
    'p.auth@class' : function(attr) { return !attr.context.username && 'hidden' },
    'p.guest@class' : function(attr) { return !!attr.context.username && 'hidden' }
}
var flatpage_directives = {
    'h3' : 'title',
    '.content' : 'content'
}

function render_block(block, data) {
    if (typeof window[block+'_render'] == 'undefined') {
        window[block+'_render'] = $p("#"+block).compile(window[block+'_directives'])
    }
    $p("#"+block).render(data[block] || {}, window[block+'_render'])
}
function reload_callback(data) {
    console.log(data)
    var block;
    var blockDiv;
    if (data.hasOwnProperty('redirect')) {
        if ($.address.value() != data.redirect)
            $.address.value(data.redirect)
        else
            $.address.update()
    }

    for (var i=0, blocksNum=blocks.length; i<blocksNum; i++ ) {
        block = blocks[i];
        if (data.hasOwnProperty(block)) {
            blockDiv = $("#"+block)
            blockDiv.show()
            render_block(block, data)
        }
        else {
            $("#"+block).hide()
        }
    }
    render_block('instructions', data)
}
function ajax_load(url) {
    $.ajax({
        url : url,
        success : reload_callback,
        error : function(jqXHR, textStatus, errorThrown) {
            if (errorThrown == 'NOT FOUND')
                $.address.value('/')
        },
        dataType : 'json'
    })
}